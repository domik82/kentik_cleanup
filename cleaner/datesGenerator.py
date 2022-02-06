import logging
from datetime import datetime


class DatesGenerator:

    @staticmethod
    def create_comparable_date(date_dict):
        if date_dict is not None and 'year' in date_dict:
            year = date_dict['year']
        else:
            raise RuntimeError('Year is absolute minimum that needs to be defined')
        try:
            return datetime(int(year), int(date_dict.get("month", 1)), int(date_dict.get("day", 1)),
                            int(date_dict.get("hour", 0)), int(date_dict.get("minute", 0)), 0, 0)
        except Exception as e:
            logging.exception("Exception occurred while generating dates based on folder")
            raise ValueError('Provided params are not valid date')

    def comparable_dates_set(self, earliest_date):
        dates_set = {'year': self.create_comparable_date({'year': earliest_date.year}),

                     'month': self.create_comparable_date({'year': earliest_date.year,
                                                           'month': earliest_date.month}),
                     'day': self.create_comparable_date({'year': earliest_date.year,
                                                         'month': earliest_date.month,
                                                         'day': earliest_date.day}),

                     'hour': self.create_comparable_date({'year': earliest_date.year,
                                                          'month': earliest_date.month,
                                                          'day': earliest_date.day,
                                                          'hour': earliest_date.hour}),

                     'minute': self.create_comparable_date({'year': earliest_date.year,
                                                            'month': earliest_date.month,
                                                            'day': earliest_date.day,
                                                            'hour': earliest_date.hour,
                                                            'minute': earliest_date.minute})}

        return dates_set