import os
import pathlib
import random
from contextlib import contextmanager
from datetime import datetime
from timeit import default_timer

import pytest

from cleaner.dataCleaner import DataCleaner
from dataGenerators.CleanupTesterHelper import CleanupTesterHelper
from dataGenerators.configGenerator import ConfigGenerator
from dataGenerators.dataGenerator import DataGenerator

""" 
    I guess below you could try to generate "production" type of load.
    File size is adjustable. This section is commented out and I used 1kB instead or less number of devices with 1MB file.

    "Perf Tests" on fs are not really reliable.  
    
    It seems that fs mock is 2x slower compared to my SSD drive. The biggest bottleneck is folder creation.
    I didn't found any way to speed up os.makedirs
    Test for 100 devices:
        Number of generated folders: 432000
        Folder Data generation done in 209.18 seconds
        Total Device data generation done in 12.99 seconds
        Cleanup done in 177.666 seconds
        Final test folder cleanup done in 318.551 seconds
        
    Cleanup had linear execution time:
        1  device -  1.659 seconds
        2  device -  3.369 seconds
        3  device -  5.087 seconds
        4  device -  6.735 seconds
        5  device -  8.537 seconds
        10 device - 16.761 seconds
        20 device - 32.166 seconds
    
    Data generation is quite similar:
        5 Folder Data generation done in 10.71 seconds
        10 Folder Data generation done in 20.24 seconds
        20 Folder Data generation done in 41.02 seconds

    Stats from SSD:
        5 devices:
            Number of generated folders: 21600
            Folder Data generation done in 5.29 seconds
            Device data generation done in 0.37 seconds
            Cleanup done in 1.196 seconds
        10 devices:
            Number of generated folders: 43200
            Folder Data generation done in 10.08 seconds
            Device data generation done in 0.72 seconds
            Cleanup done in 2.393 seconds
    
"""


@contextmanager
def elapsed_timer():
    start = default_timer()
    elapser = lambda: default_timer() - start
    yield lambda: elapser()
    end = default_timer()
    elapser = lambda: end - start


@pytest.mark.parametrize("fast_processing", [True, False])
def test_generate_data_3_companies_with_5_devices_and_files_fast_use_predefined_date(fs, fast_processing):
    company_name = ''
    devices = []
    company_retention = 2
    end_date = datetime(2022, 1, 3, 12, 2, 0, 0)
    days_to_generate = 3
    current_working_dir = pathlib.Path().resolve()
    data_directory_name = "3_companies_with_5_devices_and_files"
    config_file_name = "config_generated.json"
    default_retention = 1
    fast_processing = fast_processing

    # generate needed data
    initial_cleanup = CleanupTesterHelper(company_name, devices, company_retention, end_date, days_to_generate,
                                          current_working_dir, data_directory_name, config_file_name)

    print(f"\r\n Test Start")
    # clean folder
    with elapsed_timer() as elapsed:
        initial_cleanup.clean_up()
        print(f"Test folder cleanup done in {elapsed():.3f} seconds")

    assert not os.path.exists(initial_cleanup.full_data_dir)

    # generate needed data
    companies = ['CompanyA_3d', 'CompanyB_3d', 'CompanyC_3d']
    number_of_devices = 5
    number_of_files = 50
    # file_size = 1024 * 1024  # 1MB -> 1024  # 1kB
    file_size = 1024  # 1MB -> 1024  # 1kB

    data_gen_helpers = {}
    cleanup_tester_helpers = {}
    for company in companies:
        # generate all company data
        cleanup_tester_helper = CleanupTesterHelper(company, [], company_retention, end_date, days_to_generate,
                                                    current_working_dir, data_directory_name, config_file_name)

        data_generator = DataGenerator(company, [], cleanup_tester_helper.start_date,
                                       cleanup_tester_helper.days_to_generate,
                                       cleanup_tester_helper.data_directory)

        data_generator.company_name = company
        data_generator.devices = data_generator.generate_list_of_devices(number_of_devices)
        cleanup_tester_helper.company_name = company
        cleanup_tester_helper.devices = data_generator.devices

        data_gen_helpers[company] = data_generator
        cleanup_tester_helpers[company] = cleanup_tester_helper

        with elapsed_timer() as elapsed:
            data_generator.generate_and_write()
            print(f"Folder Data generation done in {elapsed():.2f} seconds")
            ############
            # generate files inside device folder
            with elapsed_timer() as d_elapsed:
                for device in data_generator.devices:
                    full_device_dir = cleanup_tester_helper.generate_full_device_dir(device)
                    not_existing_device_dir = data_generator.generate_full_folder_date_by_params(
                        cleanup_tester_helper.generate_first_not_existing_folder_date(),
                        full_device_dir)
                    file_list = data_generator.generate_random_files(not_existing_device_dir, device, file_size,
                                                                     number_of_files)
                    for file in file_list:
                        assert os.path.exists(file)
                    print(f"Device data generation done in {d_elapsed():.2f} seconds")

    for company in companies:
        # start to check random device folder to make test faster (retention is same for all)
        random_device = random.choice(data_gen_helpers[company].devices)
        full_device_dir = cleanup_tester_helpers[company].generate_full_device_dir(random_device)
        not_existing_device_dir = data_gen_helpers[company].generate_full_folder_date_by_params(
            cleanup_tester_helpers[company].generate_first_not_existing_folder_date(),
            full_device_dir)

        device_folder_should_exist_date_dir = data_gen_helpers[company].generate_full_folder_date_by_params(
            cleanup_tester_helpers[company].generate_first_existing_folder_date(),
            full_device_dir)

        # check existence before cleanup
        assert os.path.exists(not_existing_device_dir)
        assert os.path.exists(device_folder_should_exist_date_dir)

        # check existence before cleanup
        assert os.path.exists(not_existing_device_dir)
        assert os.path.exists(device_folder_should_exist_date_dir)

    # generate needed config file
    company_retentions = {}
    for company in companies:
        company_retentions[company] = cleanup_tester_helpers[company].company_retention

    config_generator = ConfigGenerator()
    generated_config = config_generator.generate_configuration(default_retention, company_retentions)

    config_generator.write_configuration(initial_cleanup.full_config_dir, generated_config)

    # execute cleanup
    data_cleaner = DataCleaner(initial_cleanup.full_data_dir, initial_cleanup.full_config_dir,
                               fast_processing,
                               initial_cleanup.end_date)

    with elapsed_timer() as elapsed:
        data_cleaner.process_data_dir()
        print(f"Cleanup done in {elapsed():.3f} seconds")

    for company in companies:
        # start to check random device folder
        random_device = random.choice(data_gen_helpers[company].devices)
        full_device_dir = cleanup_tester_helpers[company].generate_full_device_dir(random_device)
        not_existing_device_dir = data_gen_helpers[company].generate_full_folder_date_by_params(
            cleanup_tester_helpers[company].generate_first_not_existing_folder_date(),
            full_device_dir)

        device_folder_should_exist_date_dir = data_gen_helpers[company].generate_full_folder_date_by_params(
            cleanup_tester_helpers[company].generate_first_existing_folder_date(),
            full_device_dir)

        # check existence after cleanup
        assert not os.path.exists(not_existing_device_dir)
        assert os.path.exists(device_folder_should_exist_date_dir)

    # clean folder
    with elapsed_timer() as elapsed:
        initial_cleanup.clean_up()
        print(f"Final test folder cleanup done in {elapsed():.3f} seconds")
    print(f"\r\n Test Stop")
