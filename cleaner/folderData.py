import copy
import logging
import os
import shutil

from cleaner.datesGenerator import DatesGenerator


def log_dir_on_error(action, name, exc):
    logging.error(f'shutil.rmtree fail - can\'t remove folder {name}')

class FolderData:
    def __init__(self, folder, folder_type, folder_date_dict, folder_retention_date, folder_fast_process):
        self.folder_dir_entry = folder
        self.folder_retention_date = folder_retention_date
        self.folder_type = folder_type
        self.folder_path_dates = folder_date_dict
        self.sub_folder_list = []
        # self.folder_fast_process = True
        self.folder_fast_process = folder_fast_process
        self.dates_generator = DatesGenerator()

    @staticmethod
    def remove_folder(path):
        try:
            logging.info(f'DELETING folder: {path}')
            if not shutil.rmtree(path, onerror=log_dir_on_error):
                logging.info(f"{path} is removed successfully")
            else:
                logging.error(f"Unable to delete the {path}")
        except PermissionError:
            logging.error(f"Unable to delete the {path}, PermissionError")

    def process_folder(self):
        logging.info(f'Start folder processing -- {self.folder_dir_entry.path}')

        self.folder_path_dates[self.folder_type] = self.folder_dir_entry.name
        try:
            folder_date = self.dates_generator.create_comparable_date(self.folder_path_dates)
        except ValueError:
            logging.error(f'Folder is not a valid date {self.folder_dir_entry.path}')
            return

        folder_retention_date = self.folder_retention_date[self.folder_type]
        logging.info(
            f'Folder type: {str(self.folder_type)},  folder_date {str(folder_date)} - folder_retention_date {str(folder_retention_date)}')

        if folder_date < folder_retention_date and (self.folder_fast_process or self.folder_type == 'minute'):
            self.remove_folder(self.folder_dir_entry.path)
        elif folder_date <= folder_retention_date:
            with os.scandir(self.folder_dir_entry.path) as scanner:
                delete_empty_folder = True
                for entry in scanner:
                    # os.scandir has to have at least one element to asses if folder is not empty
                    # I didn't wanted to execute scandir multiple times to check it
                    # empty folders will be deleted execution by execution (max 4) -  hour / day / month / year
                    # using fast_process will handle such cases properly
                    delete_empty_folder = False
                    logging.info(f'Sub folder to process: {entry.path}')
                    if not entry.name.startswith('.') and entry.is_dir():
                        folder_date = copy.deepcopy(self.folder_path_dates)
                    folder_date[self.folder_type] = self.folder_dir_entry.name
                    folder_data = FolderData(entry, self.get_child_folder_type(self.folder_type), folder_date,
                                             self.folder_retention_date, self.folder_fast_process)
                    self.sub_folder_list.append(folder_data)

            if delete_empty_folder:
                self.remove_folder(self.folder_dir_entry.path)

        logging.info(f'End folder processing -- {self.folder_dir_entry.path}')
        return self.sub_folder_list

    @staticmethod
    def get_child_folder_type(parent_folder_type):
        parent_child_pattern = {'company': 'device', 'device': 'year', 'year': 'month', 'month': 'day', 'day': 'hour',
                                'hour': 'minute', 'minute': None}

        if parent_folder_type is not None and parent_folder_type in parent_child_pattern:
            return parent_child_pattern[parent_folder_type]
        else:
            raise ValueError('Provided folder type is not valid')
