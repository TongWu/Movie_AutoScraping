import os
import re
import sys
import time


def is_valid_file_size(file_path, size_limit):
    """Check file size limit"""
    return os.path.getsize(file_path) < size_limit


def clean_filename(filename, c, no, u, uc):
    """Clean the file name"""

    # Delete number prefix, e.g., 232GANA-334-C.mp4 -> GANA-334-C.mp4
    filename = re.sub(r"^\d+", "", filename)

    # Delete [], e.g., [233.com]SSNI-334-C.mp4 -> SSNI-334-C.mp4
    filename = re.sub(r"^\[.*?\]", "", filename)

    # Add "-", e.g., SSNI334C.mp4 -> SSNI-334-C.mp4
    if re.match(r"[A-Za-z]+\d+C\.", filename):
        filename = re.sub(r"([A-Za-z]+)(\d+)(C\.)", r"\1-\2-\3", filename)
    elif re.match(r"[A-Za-z]+\d+-C\.", filename):
        filename = re.sub(r"([A-Za-z]+)(\d+)-C\.", r"\1-\2-C.", filename)
    elif re.match(r"[A-Za-z]+\d\.", filename):
        filename = re.sub(r"([A-Za-z]+)(\d+)", r"\1-\2", filename)

    # Delete all characters after the number part
    filename = re.sub(r"(\d+)-?[^-.]+(?=\.[^.]+$)", r"\1", filename)

    if c:
        # Add "-C" if it is not exist, e.g., SSNI-334.mp4 -> SSNI-334-C.mp4
        if not re.search(r"-c\.(?=[^.]+$)", filename, re.I):  # re.I 是大小写不敏感标志
            filename = re.sub(r"\.(?=[^.]+$)", "-C.", filename)
    elif no:
        return filename
    elif u:
        # Delete all characters after -u but before .extension
        # filename = re.sub(r"(-u).*\.", r"\1.", filename, re.I)
        # Change all -u tag to -hack tag
        # filename = re.sub(r"-u", "-hack", filename, re.I)

        # Add -hack tag
        filename = re.sub(r"\.(?=[^.]+$)", "-hack.", filename)
    elif uc:
        # Change the possible pattern (-u-c, -c-u, -uc, -cu) to -hack-c
        # filename = re.sub(r"-(u-c|c-u|uc|cu|hack-c|hackc)(?=\.[^.]+$)", "-hack-c", filename)

        # Add -hack-c tag
        filename = re.sub(r"\.(?=[^.]+$)", "-hack-c.", filename)

    return filename


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


def main(dry_run, folder_path, c, no, u, uc):
    # 500Mb by default
    size_limit = 500 * 1024 * 1024

    for dirpath, dirnames, filenames in os.walk(folder_path):
        for file_name in filenames:
            file_path = os.path.join(dirpath, file_name)

            if not is_video_file(file_name):
                continue

            # Detect size
            if os.path.isfile(file_path) and is_valid_file_size(file_path, size_limit):
                if dry_run:
                    print(f"File '{file_name}' will be deleted")
                else:
                    os.remove(file_path)
                    print(f"Deleted a file less than 500Mb: {file_name}")
                continue

            # Clean the filename
            # TODO: Output a txt file with the log
            cleaned_filename = clean_filename(file_name, c, no, u, uc)
            if cleaned_filename != file_name:
                if dry_run:
                    print(f"'{file_name}'\t\t->\t\t'{cleaned_filename}'")
                else:
                    new_file_path = os.path.join(dirpath, cleaned_filename)
                    os.rename(file_path, new_file_path)
                    print(f"File name changed from '{file_name}'\t\tto\t\t'{cleaned_filename}'")
            else:
                if dry_run:
                    print(f"'{file_name}' -> NO CHANGE")


import argparse
import subprocess
import configparser


def modify_config(c, f, o):
    config = configparser.ConfigParser()

    # Read config.ini
    config.read(c + 'config.ini')
    if not f.endswith('/'):
        f += '/'
    failed_output_folder = f + "fail"

    config['common']['source_folder'] = f
    config['common']['success_output_folder'] = o
    config['common']['failed_output_folder'] = failed_output_folder

    with open('./config.ini', 'w') as configfile:
        config.write(configfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process video files.')
    parser.add_argument('-s', '--source', type=str, required=True, help='Source folder path')
    parser.add_argument('-dp', '--destination', type=str, required=True, help='Success output folder path')
    parser.add_argument('-m', '--mdc', type=str, required=True, help='MDC file path')
    parser.add_argument('-d', '--dryrun', action='store_true', help='Enable dry run mode')
    parser.add_argument('-c', '--sub', action='store_true', help='Scrape all movies default with subtitle')
    parser.add_argument('-no', '--no_sub', action='store_true', help='Scrape all movies default with NO subtitle')
    parser.add_argument('-u', '--hack', action='store_true', help='Scrape all movies default with hacked')
    parser.add_argument('-uc', '--hack_sub', action='store_true', help='Scrape all movies default with hacked AND '
                                                                       'subtitle')

    args = parser.parse_args()

    if sum([args.c, args.u, args.uc, args.no]) != 1:
        print("Error: You must provide exactly one of the following options: -c, -no, -u, -uc")
        sys.exit()

    # Fetch arguments
    option_c = args.c
    option_no = args.no
    option_u = args.u
    option_uc = args.uc

    folder_path = args.source
    success_output_path = args.destination
    mdc_path = args.mdc
    if not mdc_path.endswith('/'):
        mdc_path += '/'
    config_path = mdc_path

    # Check the path existing
    if not os.path.exists(folder_path):
        print("The path is not exist, exit.")
        sys.exit()

    # Check dry run
    dry_run = args.dryrun
    if dry_run:
        print("DRY RUN, will not affect the file")
    else:
        print("The program will modify these files:")

    # Whatever the dry run option, run dry run first
    main(True, folder_path, option_c, option_no, option_u, option_uc)

    if not dry_run:
        try:
            countdown(10)
        except KeyboardInterrupt:
            print("\nOperation interrupted by user, abort.")
            sys.exit()
        main(False, folder_path, option_c, option_no, option_u, option_uc)

    """ Modify the MDC configuration file """
    modify_config(config_path, folder_path, success_output_path)

    """ Run MDC """
    try:
        subprocess.run([mdc_path + 'mdc'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while running mdc: {e}")