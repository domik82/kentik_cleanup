import os
import shutil
from datetime import timedelta
from stat import S_IWRITE


def remove_readonly(func, path, exc_info):
    """Clear the readonly bit and reattempt the removal"""
    # ERROR_ACCESS_DENIED = 5
    if func not in (os.unlink, os.rmdir) or exc_info[1].winerror != 5:
        raise exc_info[1]
    os.chmod(path, S_IWRITE)
    func(path)


class CleanupTesterHelper:

    def __init__(self, company_name, devices, company_retention, end_date, days_to_generate, working_directory,
                 data_directory,
                 config_file_name):
        self.company_name = company_name
        self.devices = devices
        self.company_retention = company_retention
        self.end_date = end_date
        self.days_to_generate = days_to_generate
        self.working_directory = working_directory
        self.data_directory = data_directory
        self.config_file_name = config_file_name

        self.start_date = self.generate_start_date()
        self.retention_date = self.generate_retention_date()
        self.full_data_dir = self.generate_full_data_dir()
        self.full_config_dir = self.generate_full_config_dir()

    def generate_start_date(self):
        return self.end_date - timedelta(days=self.days_to_generate)

    def generate_retention_date(self):
        return self.end_date - timedelta(days=self.company_retention)

    def generate_first_not_existing_folder_date(self):
        """ Generate first date that is before retention date """
        return self.end_date - timedelta(days=self.company_retention) - timedelta(minutes=1)

    def generate_first_existing_folder_date(self):
        """ Generate first date that is after retention date """
        return self.end_date - timedelta(days=self.company_retention) + timedelta(minutes=1)

    def generate_full_data_dir(self):
        return os.path.join(self.working_directory, self.data_directory)

    def generate_full_config_dir(self):
        return os.path.join(self.working_directory, self.data_directory, self.config_file_name)

    def generate_full_device_dir(self, device):
        return os.path.join(self.full_data_dir, self.company_name, device)

    def clean_data_dir(self):
        if os.path.exists(os.path.abspath(self.full_data_dir)):
            shutil.rmtree(os.path.abspath(self.full_data_dir), onerror=remove_readonly)

    def clean_config_dir(self):
        if os.path.exists(os.path.abspath(self.full_config_dir)):
            shutil.rmtree(os.path.abspath(self.full_config_dir), onerror=remove_readonly)

    def clean_up(self):
        self.clean_data_dir()
        self.clean_config_dir()

