import os
import re
import sys
import time
import datetime
import argparse
import subprocess
import configparser
import file_clean

def countdown(seconds):
    """Show countdown"""
    print("==========================================================================================================")
    print("You will have 10 seconds to review the change list, if something went wrong or the list is long, please\n"
          + "use CTRL+C to review the list, the program has dry run with argument -d or --dryrun.")
    print("==========================================================================================================")
    for i in range(seconds, 0, -1):
        sys.stdout.write(f"\rWait for {i} sec...")
        sys.stdout.flush()
        time.sleep(1)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process video files.')
    # parser.add_argument('-s', '--source', type=str, required=True, help='Source folder path')
    # parser.add_argument('-dp', '--destination', type=str, required=True, help='Success output folder path')
    # parser.add_argument('-m', '--mdc', type=str, required=True, help='MDC file path')
    parser.add_argument('-d', '--dryrun', action='store_true', help='Enable dry run mode')
    parser.add_argument('-c', '--sub', action='store_true', help='Scrape all movies default with subtitle')
    parser.add_argument('-no', '--no_sub', action='store_true', help='Scrape all movies default with NO subtitle')
    parser.add_argument('-u', '--hack', action='store_true', help='Scrape all movies default with hacked')
    parser.add_argument('-uc', '--hack_sub', action='store_true', help='Scrape all movies default with hacked AND '
                                                                       'subtitle')
    """ Step 1: Fetch arguments and initialise """
    print("Initialising...")
    args = parser.parse_args()

    if sum([args.sub, args.no_sub, args.hack, args.hack_sub]) != 1:
        print("Error: You must provide exactly one of the following options: -c, -no, -u, -uc")
        input_from_command = input("Specify your command in here: (d, c, no, u, uc)\n")
        if input_from_command == 'd':
            args.dryrun = True
        elif input_from_command == 'c':
            args.sub = True
        elif input_from_command == 'no':
            args.no_sub = True
        elif input_from_command == 'u':
            args.hack = True
        elif input_from_command == 'uc':
            args.hack_sub = True
        else:
            print("No valid command, exit...")
            sys.exit()

    # Load the configuration from MAS_config.ini
    config = configparser.ConfigParser()
    config.read('MAS_config.ini', encoding='utf-8')

    '''
    mdc_path = config['general']['mdc']
    if not mdc_path.endswith('/'):
        mdc_path += '/'
    mdc_config_path = mdc_path
    '''

    if args.sub:
        folder_path = config['sub']['source']
        success_output_path = config['sub']['dest']
    elif args.no_sub:
        folder_path = config['no_sub']['source']
        success_output_path = config['no_sub']['dest']
    elif args.hack:
        folder_path = config['hack']['source']
        success_output_path = config['hack']['dest']
    elif args.hack_sub:
        folder_path = config['hack_sub']['source']
        success_output_path = config['hack_sub']['dest']
    else:
        print("No specify path, exit...")
        sys.exit()

    # Check the path existing
    if not os.path.exists(folder_path):
        print("The path is not exist, exit.")
        sys.exit()
        
    if not folder_path.endswith('/'):
        folder_path += '/'

    if not folder_path.endswith('/'):
        folder_path += '/'

    # Check dry run
    dry_run = args.dryrun
    if dry_run:
        print(
            "=========================================================================================================="
        )
        print("DRY RUN, will not affect the file")
        print(
            "=========================================================================================================="
        )
    else:
        print(
            "=========================================================================================================="
        )
        print("The program will make affect on modifications and/or deletions")
        print(
            "=========================================================================================================="
        )

    """ Step 1 Finished """
    print("\n\nFinished\n\n")

    """ Step 2: Dry run and log """
    # Whatever the dry run option, run dry run first
    print("Generate file report...\n\n")
    file_clean(True, folder_path, args.sub, args.no_sub, args.hack, args.hack_sub)

    if dry_run:
        sys.exit()
    else:
        try:
            countdown(10)
        except KeyboardInterrupt:
            print("\nOperation interrupted by user, abort.")
            sys.exit()
        file_clean(False, folder_path, args.sub, args.no_sub, args.hack, args.hack_sub)

    print("Finished\n\n")

    """ Run MDC """
    """
    print("Run MDC\n\n")
    try:
        os.system(
            f"{mdc_path}mdc -C 'common:source_folder={folder_path}' -C 'common:failed_output_folder={folder_path}failed' -C 'common:success_output_folder={success_output_path}' ")
    except subprocess.CalledProcessError as e:
        print(f"Error while running mdc: {e}")

    print("Finished")
    """

