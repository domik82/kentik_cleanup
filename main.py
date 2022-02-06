import argparse
import sys
from distutils import util
from datetime import datetime

from cleaner.dataCleaner import DataCleaner

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process data folder and clean it up')
    parser.add_argument('-d', '--data', help='Path to data', required=True, default='/data')
    parser.add_argument('-c', '--config', help='Path to config file', required=True, default='/config/config.json')
    parser.add_argument('-q', '--quick',
                        help='Process data faster by deleting folders from top. Use with caution. Might generate '
                             'bigger IO on disk. By default slower processing will be used (minute by minute).',
                        required=False, default=False)
    parser.add_argument('-t', '--time', help='Unix Timestamp', required=False)

    args = parser.parse_args()

    if args.time:
        try:
            current_time = datetime.fromtimestamp(int(args.time))
        except ValueError:
            print(f'Please provide valid timestamp value. Provided: {args.time}')
            sys.exit(1)
    else:
        current_time = datetime.now()

    quick = False
    if args.quick:
        try:
            quick = bool(util.strtobool(args.quick))
        except ValueError:
            print(f'Please provide valid quick param value. Provided: {args.quick}')
            sys.exit(1)

    print(
        f'Params used for processing. Data folder {args.data}, config file {args.config}, quick mode {str(quick)},'
        f' time for evaluation {current_time}')

    data_cleaner = DataCleaner(args.data, args.config, quick, current_time)
    data_cleaner.process_data_dir()
