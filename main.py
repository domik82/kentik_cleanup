import argparse
from datetime import datetime

from cleaner.dataCleaner import DataCleaner

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process data folder and clean it up')
    # parser.add_argument("-?", "--help", action="help", help="show this help message and exit")
    parser.add_argument('-d', '--data', help='Path to data', required=True, default='/data')
    parser.add_argument('-c', '--config', help='Path to config file', required=True, default='/config/config.json')
    parser.add_argument('-q', '--quick',
                        help='Process data faster by deleting folders from top. Use with caution. Might generate '
                             'bigger IO on disk. By default slower processing will be used (minute by minute).',
                        required=False, default=False)
    parser.add_argument('-t', '--time', help='Unix Timestamp', required=False)

    args = parser.parse_args()

    if args.time:
        current_time = datetime.fromtimestamp(int(args.time))
    else:
        current_time = None

    data_cleaner = DataCleaner(args.data, args.config, args.quick, current_time)
    data_cleaner.process_data_dir()
