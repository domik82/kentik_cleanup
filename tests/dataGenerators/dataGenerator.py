import os
import random
from datetime import datetime, timedelta


class DataGenerator:

    def __init__(self, company_id: str, devices: list, start_date, number_of_days, parent_directory):
        self.company_id = company_id
        self.start_date: datetime = start_date
        self.number_of_days = number_of_days
        self.devices = devices
        self.parent_directory = parent_directory
        self.list_of_generated_paths = None

    @staticmethod
    def generate_id():
        return random.randint(1, 1000)

    def generate_list_of_devices(self, number_of_devices):
        return [str(self.generate_id()) for x in range(number_of_devices)]

    @staticmethod
    def generate_datetime_range(start_date, days):
        return [start_date + timedelta(minutes=1 * x) for x in range(0, days * 24 * 60)]

    @staticmethod
    def convert_date_list_to_path(dates_list, prefix):
        return [x.strftime(prefix + '/%Y/%m/%d/%H/%M/') for x in dates_list]

    def generate_full_path(self):
        dates = self.generate_datetime_range(self.start_date, self.number_of_days)
        list_of_prefixes = [f"{self.company_id}/{x}" for x in self.devices]
        return [self.convert_date_list_to_path(dates, x) for x in list_of_prefixes]

    def write_dir_to_disk(self):
        count = 0
        for device_directory in self.list_of_generated_paths:
            for directory in device_directory:
                full_dir = os.path.normpath(os.path.join(self.parent_directory, directory))
                os.makedirs(full_dir, exist_ok=True)
                count += 1
        print(f'Number of generated folders: {count}')

    def generate_and_write(self):
        self.list_of_generated_paths = self.generate_full_path()
        self.write_dir_to_disk()

    def generate_full_folder_date_by_params(self, date, directory):
        return os.path.normpath(self.convert_date_list_to_path([date], directory)[0])

    def generate_random_binary_file(self, filename, size):
        """
        generate big binary file with the specified size in bytes
        :param filename: the filename
        :param size: the size in bytes
        :return:void
        """
        with open('%s' % filename, 'wb') as file:
            file.write(os.urandom(size))

    def generate_random_files(self, root_path, prefix, size, amount):
        generated_files = []
        for i in range(amount):
            file_path = os.path.normpath(os.path.join(root_path, f'{prefix}_{i}.bin'))
            self.generate_random_binary_file(file_path, size)
            generated_files.append(file_path)
        return generated_files
