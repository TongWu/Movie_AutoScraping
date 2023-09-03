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

            # Clean the filename
            # TODO: Output a txt file with the log
            cleaned_filename = clean_filename(file_name, c, no, u, uc)
            if cleaned_filename != file_name:
                if dry_run:
                    rename_files.append(file_name)
                    renamed_files.append(cleaned_filename)
                else:
                    new_file_path = os.path.join(dirpath, cleaned_filename)
                    os.rename(file_path, new_file_path)
                    print("Renamed " + file_name + " to " + cleaned_filename)
            else:
                if dry_run:
                    unchanged_files.append(f"{file_name}")

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
            print("The following file has NO CHANGE:")
            log_file.write("The following file has NO CHANGE:\n")

            for file_log in unchanged_files:
                print("UNCHANGE" + file_log)
                log_file.write(file_log + '\n')
            print("===================================================================================================")
            log_file.write(
                "===================================================================================================\n")

            print("The following file will RENAME:")
            log_file.write("The following file will RENAME:\n")

            for i in range(len(rename_files)):
                line = f"'{rename_files[i].ljust(max_length)}'\t->\t'{renamed_files[i]}'"
                print("(RENAME)" + line)
                log_file.write(line + '\n')
            print("===================================================================================================")
            log_file.write(
                "===================================================================================================\n")

            print("The following file will DELETE:")
            log_file.write("The following file will DELETE:\n")
            for file_log in deleted_files:
                print("(DELETE)" + file_log)
                log_file.write(file_log + '\n')
        print("===================================================================================================")


def modify_config(c, f, o):
    config = configparser.ConfigParser()

    # Read config.ini
    config.read(c + 'config.ini')
    if not f.endswith('/'):
        f += '/'
    failed_output_folder = f + "failed"

    config['common']['source_folder'] = f
    config['common']['success_output_folder'] = o
    config['common']['failed_output_folder'] = failed_output_folder

    with open('./config.ini', 'w') as configfile:
        config.write(configfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process video files.')
    #parser.add_argument('-s', '--source', type=str, required=True, help='Source folder path')
    #parser.add_argument('-dp', '--destination', type=str, required=True, help='Success output folder path')
    #parser.add_argument('-m', '--mdc', type=str, required=True, help='MDC file path')
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

    # Load the configuration from config.ini
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    mdc_path = config['common']['mdc']
    mdc_config_path = mdc_path
    if not mdc_path.endswith('/'):
        mdc_path += '/'

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
    main(True, folder_path, args.sub, args.no_sub, args.hack, args.hack_sub)

    if dry_run:
        sys.exit()
    else:
        try:
            countdown(10)
        except KeyboardInterrupt:
            print("\nOperation interrupted by user, abort.")
            sys.exit()
        main(False, folder_path, args.sub, args.no_sub, args.hack, args.hack_sub)

    print("Finished\n\n")

    """ Step 3: Modify the MDC configuration file """
    print("Modifying the MDC configuration file...\n\n")
    modify_config(mdc_config_path, folder_path, success_output_path)
    print("Finished\n\n")

    """ Run MDC """
    print("Run MDC\n\n")
    try:
        subprocess.run([mdc_path + 'mdc'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while running mdc: {e}")

    print("Finished")
