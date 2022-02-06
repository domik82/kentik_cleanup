import os
import pathlib
import shutil
from contextlib import contextmanager
from datetime import datetime, timedelta
from stat import S_IRGRP, S_IROTH, S_IREAD, S_IWRITE
from timeit import default_timer

from cleaner.configuration import Configuration
from cleaner.dataCleaner import DataCleaner
from dataGenerators.CleanupTesterHelper import CleanupTesterHelper
from dataGenerators.configGenerator import ConfigGenerator
from dataGenerators.dataGenerator import DataGenerator


# Below tests are generating mainly folders
# I didn't wanted to wear down disk to much by creating files just to delete those second later
# I found pyfakefs https://github.com/jmcgeheeiv/pyfakefs/ that mocks disk operations.
# To run it on actual disk just remove fs param from def

# If that would meant to be a test for "production" code I would think about
# using RAM disk for such purpose as I think such unit tests might wear down disk

@contextmanager
def elapsed_timer():
    start = default_timer()
    elapser = lambda: default_timer() - start
    yield lambda: elapser()
    end = default_timer()
    elapser = lambda: end - start


def test_generate_data_single_company_and_2devices_minute_by_minute_random_date(fs):
    company_name = 'CompanyA_3d'
    devices = ['A1A', 'A1B']
    company_retention = 2
    end_date = datetime.today()
    days_to_generate = 3
    current_working_dir = pathlib.Path().resolve()
    data_directory_name = "data_single_company_and_2devices"
    config_file_name = "config_generated.json"
    default_retention = 1
    fast_processing = False

    # generate needed data
    cleanup_tester_helper = CleanupTesterHelper(company_name, devices, company_retention, end_date, days_to_generate,
                                                current_working_dir, data_directory_name, config_file_name)

    print(f"\r\n Test Start")
    # clean folder
    with elapsed_timer() as elapsed:
        cleanup_tester_helper.clean_up()
        print(f"Test folder cleanup done in {elapsed():.3f} seconds")

    assert not os.path.exists(cleanup_tester_helper.full_data_dir)

    # generate needed data
    data_generator = DataGenerator(cleanup_tester_helper.company_name, cleanup_tester_helper.devices,
                                   cleanup_tester_helper.start_date, cleanup_tester_helper.days_to_generate,
                                   cleanup_tester_helper.data_directory)
    with elapsed_timer() as elapsed:
        data_generator.generate_and_write()
        print(f"Data generation done in {elapsed():.3f} seconds")

    # generate needed config file
    config_generator = ConfigGenerator()
    generated_config = config_generator.generate_configuration(default_retention, {
        cleanup_tester_helper.company_name: cleanup_tester_helper.company_retention})

    config_generator.write_configuration(cleanup_tester_helper.full_config_dir, generated_config)

    # start to check device folder
    full_first_device_dir = cleanup_tester_helper.generate_full_device_dir(cleanup_tester_helper.devices[0])
    non_existent_first_device_dir = data_generator.generate_full_folder_date_by_params(
        cleanup_tester_helper.generate_first_not_existing_folder_date(),
        full_first_device_dir)

    should_exist_first_device_dir = data_generator.generate_full_folder_date_by_params(
        cleanup_tester_helper.generate_first_existing_folder_date(),
        full_first_device_dir)

    # check existence before cleanup
    assert os.path.exists(non_existent_first_device_dir)
    assert os.path.exists(should_exist_first_device_dir)

    full_second_device_dir = cleanup_tester_helper.generate_full_device_dir(cleanup_tester_helper.devices[1])
    non_existent_second_device_dir = data_generator.generate_full_folder_date_by_params(
        cleanup_tester_helper.generate_first_not_existing_folder_date(),
        full_second_device_dir)

    should_exist_second_device_dir = data_generator.generate_full_folder_date_by_params(
        cleanup_tester_helper.generate_first_existing_folder_date(),
        full_second_device_dir)

    # check existence before cleanup
    assert os.path.exists(non_existent_second_device_dir)
    assert os.path.exists(should_exist_second_device_dir)

    # execute cleanup
    data_cleaner = DataCleaner(cleanup_tester_helper.full_data_dir, cleanup_tester_helper.full_config_dir,
                               fast_processing,
                               cleanup_tester_helper.end_date)
    with elapsed_timer() as elapsed:
        data_cleaner.process_data_dir()
        print(f"Cleanup done in {elapsed():.3f} seconds")

    assert not os.path.exists(non_existent_first_device_dir)
    assert os.path.exists(should_exist_first_device_dir)
    assert not os.path.exists(non_existent_second_device_dir)
    assert os.path.exists(should_exist_second_device_dir)

    # clean folder
    with elapsed_timer() as elapsed:
        cleanup_tester_helper.clean_up()
        print(f"Final test folder cleanup done in {elapsed():.3f} seconds")
    print(f"\r\n Test Stop")


def test_generate_data_single_company_and_1device_fast_use_predefined_date(fs):
    company_name = 'CompanyA_3d'
    devices = ['A1A']
    company_retention = 2
    end_date = datetime(2022, 1, 3, 12, 2, 0, 0)
    days_to_generate = 3
    current_working_dir = pathlib.Path().resolve()
    data_directory_name = "data_single_company_and_1device"
    config_file_name = "config_generated.json"
    default_retention = 1
    fast_processing = True

    # generate needed data
    cleanup_tester_helper = CleanupTesterHelper(company_name, devices, company_retention, end_date, days_to_generate,
                                                current_working_dir, data_directory_name, config_file_name)

    print(f"\r\n Test Start")
    # clean folder
    with elapsed_timer() as elapsed:
        cleanup_tester_helper.clean_up()
        print(f"Test folder cleanup done in {elapsed():.3f} seconds")

    assert not os.path.exists(cleanup_tester_helper.full_data_dir)

    # generate needed data
    data_generator = DataGenerator(cleanup_tester_helper.company_name, cleanup_tester_helper.devices,
                                   cleanup_tester_helper.start_date, cleanup_tester_helper.days_to_generate,
                                   cleanup_tester_helper.data_directory)
    with elapsed_timer() as elapsed:
        data_generator.generate_and_write()
        print(f"Data generation done in {elapsed():.2f} seconds")

    # generate needed config file
    config_generator = ConfigGenerator()
    generated_config = config_generator.generate_configuration(default_retention, {
        cleanup_tester_helper.company_name: cleanup_tester_helper.company_retention})
    config_generator.write_configuration(cleanup_tester_helper.full_config_dir, generated_config)

    # start to check device folder
    full_device_dir = cleanup_tester_helper.generate_full_device_dir(cleanup_tester_helper.devices[0])
    device_folder_shouldnt_exist_dir = data_generator.generate_full_folder_date_by_params(
        cleanup_tester_helper.generate_first_not_existing_folder_date(),
        full_device_dir)

    device_folder_should_exist_date_dir = data_generator.generate_full_folder_date_by_params(
        cleanup_tester_helper.generate_first_existing_folder_date(),
        full_device_dir)

    # check existence before cleanup
    assert os.path.exists(device_folder_shouldnt_exist_dir)
    assert os.path.exists(device_folder_should_exist_date_dir)

    # execute cleanup
    data_cleaner = DataCleaner(cleanup_tester_helper.full_data_dir, cleanup_tester_helper.full_config_dir,
                               fast_processing,
                               cleanup_tester_helper.end_date)

    with elapsed_timer() as elapsed:
        data_cleaner.process_data_dir()
        print(f"Cleanup done in {elapsed():.3f} seconds")

    assert not os.path.exists(device_folder_shouldnt_exist_dir)
    assert os.path.exists(device_folder_should_exist_date_dir)

    # With fast processing whole structure like year/month/day should be removed on first run
    day_folder_shouldnt_exist_date = end_date - timedelta(days=days_to_generate) + timedelta(minutes=1)
    day_folder_shouldnt_exist_date_dir = data_generator.generate_full_folder_date_by_params(
        day_folder_shouldnt_exist_date,
        full_device_dir)

    path_year = pathlib.Path(day_folder_shouldnt_exist_date_dir).parent.parent.parent.parent.absolute()
    assert not os.path.exists(path_year)

    # clean folder
    with elapsed_timer() as elapsed:
        cleanup_tester_helper.clean_up()
        print(f"Final test folder cleanup done in {elapsed():.3f} seconds")
    print(f"\r\n Test Stop")


def test_generate_data_single_company_and_1device_minute_by_minute_predefined_date(fs):
    company_name = 'CompanyA_3d'
    devices = ['A1A']
    company_retention = 2
    end_date = datetime(2022, 1, 3, 12, 2, 0, 0)
    days_to_generate = 3
    current_working_dir = pathlib.Path().resolve()
    data_directory_name = "data_single_company_and_1device"
    config_file_name = "config_generated.json"
    default_retention = 1
    fast_processing = False

    # generate needed data
    cleanup_tester_helper = CleanupTesterHelper(company_name, devices, company_retention, end_date, days_to_generate,
                                                current_working_dir, data_directory_name, config_file_name)

    print(f"\r\n Test Start")
    # clean folder
    with elapsed_timer() as elapsed:
        cleanup_tester_helper.clean_up()
        print(f"Test folder cleanup done in {elapsed():.3f} seconds")

    assert not os.path.exists(cleanup_tester_helper.full_data_dir)

    # generate needed data
    data_generator = DataGenerator(cleanup_tester_helper.company_name, cleanup_tester_helper.devices,
                                   cleanup_tester_helper.start_date, cleanup_tester_helper.days_to_generate,
                                   cleanup_tester_helper.data_directory)
    with elapsed_timer() as elapsed:
        data_generator.generate_and_write()
        print(f"Data generation done in {elapsed():.3f} seconds")

    # generate needed config file
    config_generator = ConfigGenerator()
    generated_config = config_generator.generate_configuration(default_retention, {
        cleanup_tester_helper.company_name: cleanup_tester_helper.company_retention})

    config_generator.write_configuration(cleanup_tester_helper.full_config_dir, generated_config)

    # start to check device folder
    full_device_dir = cleanup_tester_helper.generate_full_device_dir(cleanup_tester_helper.devices[0])
    device_folder_shouldnt_exist_dir = data_generator.generate_full_folder_date_by_params(
        cleanup_tester_helper.generate_first_not_existing_folder_date(),
        full_device_dir)

    device_folder_should_exist_date_dir = data_generator.generate_full_folder_date_by_params(
        cleanup_tester_helper.generate_first_existing_folder_date(),
        full_device_dir)

    # check existence before cleanup
    assert os.path.exists(device_folder_shouldnt_exist_dir)
    assert os.path.exists(device_folder_should_exist_date_dir)

    # execute cleanup
    data_cleaner = DataCleaner(cleanup_tester_helper.full_data_dir, cleanup_tester_helper.full_config_dir,
                               fast_processing,
                               cleanup_tester_helper.end_date)
    with elapsed_timer() as elapsed:
        data_cleaner.process_data_dir()
        print(f"Minute done in {elapsed():.3f} seconds")

    assert not os.path.exists(device_folder_shouldnt_exist_dir)
    assert os.path.exists(device_folder_should_exist_date_dir)

    # without fast processing it's expected that day/hour folders will stay there
    # running process second time should delete any empty hour folders
    day_folder_shouldnt_exist_date = cleanup_tester_helper.end_date - timedelta(
        days=cleanup_tester_helper.days_to_generate) + timedelta(minutes=1)

    day_folder_shouldnt_exist_date_dir = data_generator.generate_full_folder_date_by_params(
        day_folder_shouldnt_exist_date,
        full_device_dir)
    path_hour = pathlib.Path(day_folder_shouldnt_exist_date_dir).parent.absolute()

    # check existence before cleanup
    assert os.path.exists(path_hour)

    with elapsed_timer() as elapsed:
        data_cleaner.process_data_dir()
        print(f"Hour Cleanup done at {elapsed():.3f} seconds")

    assert not os.path.exists(path_hour)

    # running third time should delete any empty day folder
    path_day = pathlib.Path(day_folder_shouldnt_exist_date_dir).parent.parent.absolute()
    # check existence before cleanup
    assert os.path.exists(path_day)

    with elapsed_timer() as elapsed:
        data_cleaner.process_data_dir()
        print(f"Day Cleanup done at {elapsed():.3f} seconds")

    assert not os.path.exists(path_day)

    # running forth time should delete any empty month folder
    path_month = pathlib.Path(day_folder_shouldnt_exist_date_dir).parent.parent.parent.absolute()
    # check existence before cleanup
    assert os.path.exists(path_month)

    with elapsed_timer() as elapsed:
        data_cleaner.process_data_dir()
        print(f"Month Cleanup done at {elapsed():.3f} seconds")

    assert not os.path.exists(path_month)

    # running fifth time should delete any empty year folder
    path_year = pathlib.Path(day_folder_shouldnt_exist_date_dir).parent.parent.parent.parent.absolute()
    # check existence before cleanup
    assert os.path.exists(path_year)

    with elapsed_timer() as elapsed:
        data_cleaner.process_data_dir()
        print(f"Year Cleanup done at {elapsed():.3f} seconds")

    assert not os.path.exists(path_year)

    # clean folder
    with elapsed_timer() as elapsed:
        cleanup_tester_helper.clean_up()
        print(f"Final test folder cleanup done in {elapsed():.3f} seconds")
    print(f"\r\n Test Stop")


def test_generate_data_single_company_and_1device_fast_use_predefined_date_read_only_folder(fs):
    company_name = 'CompanyA_3d'
    devices = ['A1A']
    company_retention = 2
    end_date = datetime(2022, 1, 3, 12, 2, 0, 0)
    days_to_generate = 3
    current_working_dir = pathlib.Path().resolve()
    data_directory_name = "data_single_company_and_1device_read_only"
    config_file_name = "config_generated.json"
    default_retention = 1
    fast_processing = True

    # generate needed data
    cleanup_tester_helper = CleanupTesterHelper(company_name, devices, company_retention, end_date, days_to_generate,
                                                current_working_dir, data_directory_name, config_file_name)

    print(f"\r\n Test Start")
    # clean folder
    with elapsed_timer() as elapsed:
        cleanup_tester_helper.clean_up()
        print(f"Test folder cleanup done in {elapsed():.3f} seconds")

    assert not os.path.exists(cleanup_tester_helper.full_data_dir)

    # generate needed data
    data_generator = DataGenerator(cleanup_tester_helper.company_name, cleanup_tester_helper.devices,
                                   cleanup_tester_helper.start_date, cleanup_tester_helper.days_to_generate,
                                   cleanup_tester_helper.data_directory)
    with elapsed_timer() as elapsed:
        data_generator.generate_and_write()
        print(f"Data generation done in {elapsed():.2f} seconds")

    # generate needed config file
    config_generator = ConfigGenerator()
    generated_config = config_generator.generate_configuration(default_retention, {
        cleanup_tester_helper.company_name: cleanup_tester_helper.company_retention})
    config_generator.write_configuration(cleanup_tester_helper.full_config_dir, generated_config)

    # start to check device folder
    full_device_dir = cleanup_tester_helper.generate_full_device_dir(cleanup_tester_helper.devices[0])
    non_existent_folder_based_on_retention = data_generator.generate_full_folder_date_by_params(
        cleanup_tester_helper.generate_first_not_existing_folder_date(),
        full_device_dir)

    # make folder read only
    data_file = 'read_only_data_file.txt'

    with open(os.path.join(non_existent_folder_based_on_retention, data_file), 'w') as f:
        f.write('This is data file!')
    os.chmod(os.path.join(non_existent_folder_based_on_retention, data_file), S_IREAD | S_IRGRP | S_IROTH)

    # Take first minute of generated data - it should normally be deleted
    first_non_existent_folder_date = end_date - timedelta(days=days_to_generate) + timedelta(minutes=1)
    first_non_existent_folder_date_dir = data_generator.generate_full_folder_date_by_params(
        first_non_existent_folder_date,
        full_device_dir)

    with open(os.path.join(first_non_existent_folder_date_dir, data_file), 'w') as f:
        f.write('This is data file!')
    os.chmod(os.path.join(first_non_existent_folder_date_dir, data_file), S_IREAD | S_IRGRP | S_IROTH)

    # Take second minute of generated data - it should normally be deleted
    second_non_existent_folder_date = end_date - timedelta(days=days_to_generate) + timedelta(minutes=2)
    second_non_existent_folder_date_dir = data_generator.generate_full_folder_date_by_params(
        second_non_existent_folder_date,
        full_device_dir)

    path_year = pathlib.Path(first_non_existent_folder_date_dir).parent.parent.parent.parent.absolute()

    # execute cleanup
    data_cleaner = DataCleaner(cleanup_tester_helper.full_data_dir, cleanup_tester_helper.full_config_dir,
                               fast_processing,
                               cleanup_tester_helper.end_date)

    # check existence before cleanup
    assert os.path.exists(non_existent_folder_based_on_retention)
    assert os.path.exists(os.path.join(non_existent_folder_based_on_retention, data_file))
    assert os.path.exists(os.path.join(first_non_existent_folder_date_dir, data_file))
    assert os.path.exists(second_non_existent_folder_date_dir)

    with elapsed_timer() as elapsed:
        data_cleaner.process_data_dir()
        print(f"Cleanup done in {elapsed():.3f} seconds")

    assert os.path.exists(non_existent_folder_based_on_retention)
    assert os.path.exists(os.path.join(non_existent_folder_based_on_retention, data_file))
    assert os.path.exists(os.path.join(first_non_existent_folder_date_dir, data_file))
    assert os.path.exists(path_year)

    # because rmtree will fail on first read only file - normally this folder would stay
    # to avoid it rmtree "onerror" operation was implemented
    # at this stage I don't really know how it should work so I'm only logging name
    assert not os.path.exists(second_non_existent_folder_date_dir)

    # clean folder
    with elapsed_timer() as elapsed:
        # Read only scenario was failing without explicit removal of read only params for fs
        # while it was working properly using disk - maybe the on_error code needs fix. Dunno.
        os.chmod(os.path.join(non_existent_folder_based_on_retention, data_file), S_IWRITE)
        os.chmod(os.path.join(first_non_existent_folder_date_dir, data_file), S_IWRITE)
        cleanup_tester_helper.clean_up()
        print(f"Final test folder cleanup done in {elapsed():.3f} seconds")
    print(f"\r\n Test Stop")


def test_generate_data_single_company_and_1device_folder_not_a_date_fast_and_slow_mode(fs):
    company_name = 'CompanyA_3d'
    devices = ['A1A']
    company_retention = 1
    end_date = datetime(2022, 1, 3, 12, 2, 0, 0)
    days_to_generate = 2
    current_working_dir = pathlib.Path().resolve()
    data_directory_name = "data_single_company_and_1device_folder_not_a_date"
    config_file_name = "config_generated.json"
    default_retention = 1
    fast_processing = False

    # generate needed data
    cleanup_tester_helper = CleanupTesterHelper(company_name, devices, company_retention, end_date, days_to_generate,
                                                current_working_dir, data_directory_name, config_file_name)

    print(f"\r\n Test Start")
    # clean folder
    with elapsed_timer() as elapsed:
        cleanup_tester_helper.clean_up()
        print(f"Test folder cleanup done in {elapsed():.3f} seconds")

    assert not os.path.exists(cleanup_tester_helper.full_data_dir)

    # generate needed data
    data_generator = DataGenerator(cleanup_tester_helper.company_name, cleanup_tester_helper.devices,
                                   cleanup_tester_helper.start_date, cleanup_tester_helper.days_to_generate,
                                   cleanup_tester_helper.data_directory)
    with elapsed_timer() as elapsed:
        data_generator.generate_and_write()
        print(f"Data generation done in {elapsed():.2f} seconds")

    # generate needed config file
    config_generator = ConfigGenerator()
    generated_config = config_generator.generate_configuration(default_retention, {
        cleanup_tester_helper.company_name: cleanup_tester_helper.company_retention})
    config_generator.write_configuration(cleanup_tester_helper.full_config_dir, generated_config)

    # start to check device folder
    full_device_dir = cleanup_tester_helper.generate_full_device_dir(cleanup_tester_helper.devices[0])

    data_file = 'file_to_retain.txt'

    # Take first minute of generated data - it should normally be deleted
    first_non_existent_folder_date = end_date - timedelta(days=days_to_generate) + timedelta(minutes=1)
    first_non_existent_folder_date_dir = data_generator.generate_full_folder_date_by_params(
        first_non_existent_folder_date,
        full_device_dir)

    with open(os.path.join(first_non_existent_folder_date_dir, data_file), 'w') as f:
        f.write('This is data file to keep!')

    bkp_folder = first_non_existent_folder_date_dir + "_bkp"
    shutil.move(first_non_existent_folder_date_dir, bkp_folder)

    assert not os.path.exists(os.path.join(first_non_existent_folder_date_dir, data_file))
    assert os.path.exists(os.path.join(bkp_folder, data_file))

    # Take second minute of generated data - it should normally be deleted
    second_non_existent_folder_date = end_date - timedelta(days=days_to_generate) + timedelta(minutes=2)
    second_non_existent_folder_date_dir = data_generator.generate_full_folder_date_by_params(
        second_non_existent_folder_date,
        full_device_dir)

    # execute cleanup
    data_cleaner = DataCleaner(cleanup_tester_helper.full_data_dir, cleanup_tester_helper.full_config_dir,
                               fast_processing,
                               cleanup_tester_helper.end_date)

    assert os.path.exists(second_non_existent_folder_date_dir)

    with elapsed_timer() as elapsed:
        data_cleaner.process_data_dir()
        print(f"Cleanup done in {elapsed():.3f} seconds")

    # folder is not getting deleted because slow mode is used and bkp_folder doesn't match date type
    assert os.path.exists(os.path.join(bkp_folder, data_file))
    assert not os.path.exists(second_non_existent_folder_date_dir)

    data_cleaner.fast_process = True
    with elapsed_timer() as elapsed:
        data_cleaner.process_data_dir()
        print(f"Cleanup done in {elapsed():.3f} seconds")

    # folder gets deleted because fast mode is used and all data inside CompanyA_3d\A1A\\2022\01\01
    # will get removed at once
    assert not os.path.exists(os.path.join(bkp_folder, data_file))

    # clean folder
    with elapsed_timer() as elapsed:
        cleanup_tester_helper.clean_up()
        print(f"Final test folder cleanup done in {elapsed():.3f} seconds")
    print(f"\r\n Test Stop")


def test_generate_config(fs):
    current_working_dir = pathlib.Path().resolve()
    config_directory = "config"
    config_file_name = "config_generated.json"
    config_dir = os.path.join(current_working_dir, config_directory)
    config_file_path = os.path.join(config_dir, config_file_name)

    if os.path.exists(config_dir):
        shutil.rmtree(os.path.abspath(config_dir))

    assert not os.path.exists(config_file_path)

    generator = ConfigGenerator()
    default_retention_policy = 10

    company_name = 'companyA'
    company_retention_policy = 30

    generated_config = generator.generate_configuration(default_retention_policy,
                                                        {company_name: company_retention_policy})
    generator.write_configuration(config_file_path, generated_config)

    config = Configuration(config_file_path)

    assert os.path.exists(config_file_path)
    assert config.get_default_retention_policy() == default_retention_policy
    assert config.get_retention_by_id(company_name) == company_retention_policy

    if os.path.exists(config_dir):
        shutil.rmtree(os.path.abspath(config_dir))

    assert not os.path.exists(config_file_path)
