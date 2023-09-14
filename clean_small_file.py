import os
import re
import sys
import time
import datetime
import argparse
import subprocess
import configparser


def is_valid_file_size(file_path, size_limit):
    """Check file size limit"""
    return os.path.getsize(file_path) < size_limit

def is_video_file(file_name):
    """Detect the file is video file or not"""
    video_extensions = ['.mp4', '.avi', '.mkv', '.flv', '.mov', '.wmv', '.rmvb']
    return any(file_name.lower().endswith(ext) for ext in video_extensions)

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

def filename_clean(dry_run, folder_path):
    # 500Mb by default
    size_limit = 500 * 1024 * 1024

    unchanged_files = []
    rename_files = []
    renamed_files = []
    deleted_files = []

    for dirpath, dirnames, filenames in os.walk(folder_path):
        for file_name in filenames:
            file_path = os.path.join(dirpath, file_name)

            # Detect size
            if os.path.isfile(file_path) and is_valid_file_size(file_path, size_limit):
                if dry_run:
                    deleted_files.append(f"{file_name}")
                else:
                    os.remove(file_path)
                    print("File '" + f"{file_name}" + "' deleted.")
                continue

            if not is_video_file(file_name):
                continue

    if dry_run:
        # Determine the log folder and file name
        log_folder = os.path.join('./', 'log')
        current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file_path = os.path.join(log_folder, f'{current_time}.log')

        # Create the log folder if it doesn't exist
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        if rename_files:
            max_length = max([len(file) for file in rename_files])
        else:
            max_length = 0

        print("Finished\n\n")

        # Print results in the desired order:
        with open(log_file_path, 'a') as log_file:
            print("The following file will DELETE:")
            log_file.write("The following file will DELETE:\n")
            for file_log in deleted_files:
                print("(DELETE) " + file_log)
                log_file.write(file_log + '\n')
        print("===================================================================================================")


def move_files_to_root(folder_path):
    """Move all files in the directory to its root."""
    for dirpath, _, filenames in os.walk(folder_path):
        for file_name in filenames:
            current_file_path = os.path.join(dirpath, file_name)
            dest_file_path = os.path.join(folder_path, file_name)

            # Check if the file is already in root, continue if so
            if current_file_path == dest_file_path:
                continue

            # Move the file
            os.rename(current_file_path, dest_file_path)
            print(f"Moved '{current_file_path}' to '{dest_file_path}'.")


def remove_empty_dirs(folder_path):
    """Remove all empty directories."""
    for dirpath, dirnames, _ in os.walk(folder_path, topdown=False):  # topdown=False, so we check from deepest level
        for dirname in dirnames:
            dir_to_check = os.path.join(dirpath, dirname)
            if not os.listdir(dir_to_check):  # Check if directory is empty
                os.rmdir(dir_to_check)
                print(f"Deleted empty directory '{dir_to_check}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process video files.')
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
        sys.exit()

    if args.sub:
        folder_path = "/home/tedwu/2016-2022/有字幕"
    elif args.no_sub:
        folder_path = "/home/tedwu/2016-2022/no_cc"
    elif args.hack:
        folder_path = "/home/tedwu/2016-2022/无码破解/no_cc"
    elif args.hack_sub:
        folder_path = "/home/tedwu/2016-2022/无码破解/有字幕"

    # Check the path existing
    if not os.path.exists(folder_path):
        print("The path is not exist, exit.")
        sys.exit()

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
    filename_clean(True, folder_path)

    if dry_run:
        sys.exit()
    else:
        try:
            countdown(10)
        except KeyboardInterrupt:
            print("\nOperation interrupted by user, abort.")
            sys.exit()
        filename_clean(False, folder_path)

        print("\nMoving files to root directory...\n")
        move_files_to_root(folder_path)
        print("\nRemoving empty directories...\n")
        remove_empty_dirs(folder_path)
    print("Finished")
