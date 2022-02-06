import logging
import os
import pathlib
from datetime import datetime, timedelta

from cleaner.configuration import Configuration
from cleaner.datesGenerator import DatesGenerator
from cleaner.folderData import FolderData

logging.basicConfig(filename='./data_cleaner.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class DataCleaner:
    config_file_path = None
    data_dir = None
    retention_setup = None

    def __init__(self, main_data_folder, config_file_path, fast_process, current_time=None):
        self.data_dir = main_data_folder
        self.config_file_path = config_file_path
        self.configuration = Configuration(self.config_file_path)
        self.fast_process = fast_process
        self.current_time = current_time
        self.dates_generator = DatesGenerator()

    @staticmethod
    def get_subdirs(path):
        """Yield directory names not starting with '.' under given path."""
        for entry in os.scandir(path):
            if not entry.name.startswith('.') and entry.is_dir():
                yield entry

    def get_data_path(self, data_path=None):
        if data_path is not None:
            return data_path
        else:
            current_working_dir = pathlib.Path().resolve()
            parent_directory = "data"
            full_dir = os.path.normpath(os.path.join(current_working_dir, "..", parent_directory, ))
            print(full_dir)
            return full_dir

    def get_retention_date_by_company(self, company_name):
        company_retention = self.configuration.get_retention_by_id_or_default(company_name)
        if self.current_time is not None:
            earliest_date = self.current_time - timedelta(days=company_retention)
        else:
            earliest_date = datetime.now() - timedelta(days=company_retention)

        retention_date = self.dates_generator.comparable_dates_set(earliest_date)
        logging.info(
            f'Processing Company: {company_name} with retention {str(company_retention)} days, expected retention date {str(earliest_date)}')
        return retention_date

    def process_data_dir(self):
        companies = [j for j in self.get_subdirs(self.data_dir)]
        for company in companies or []:
            retention_date = self.get_retention_date_by_company(company.name)
            devices = self.get_subdirs(company.path)
            # full cleanup
            for device in devices or []:
                logging.info(f'Processing Device: {device.path}')
                years = self.get_subdirs(device.path)
                folder_years = [FolderData(year, 'year', {}, retention_date, self.fast_process) for year in years if
                                years]
                for year in folder_years or []:
                    months = year.process_folder()
                    for month in months or []:
                        days = month.process_folder()
                        for day in days or []:
                            hours = day.process_folder()
                            for hour in hours or []:
                                hour = hour.process_folder()
                                for minute in hour or []:
                                    minute.process_folder()
