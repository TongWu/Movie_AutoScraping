import os
import re
import datetime


def is_valid_file_size(file_path, size_limit):
    """Check file size limit"""
    return os.path.getsize(file_path) < size_limit

def is_video_file(file_name):
    """Detect the file is video file or not"""
    video_extensions = ['.mp4', '.avi', '.mkv', '.flv', '.mov', '.wmv', '.rmvb']
    return any(file_name.lower().endswith(ext) for ext in video_extensions)

def file_clean(dry_run, folder_path, c, no, u, uc):
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
                print("(UNCHANGE) " + file_log)
                log_file.write(file_log + '\n')
            print("===================================================================================================")
            log_file.write(
                "===================================================================================================\n")

            print("The following file will RENAME:")
            log_file.write("The following file will RENAME:\n")

            for i in range(len(rename_files)):
                line = f"'{rename_files[i].ljust(max_length)}'\t->\t'{renamed_files[i]}'"
                print("(RENAME) " + line)
                log_file.write(line + '\n')
            print("===================================================================================================")
            log_file.write(
                "===================================================================================================\n")

            print("The following file will DELETE:")
            log_file.write("The following file will DELETE:\n")
            for file_log in deleted_files:
                print("(DELETE) " + file_log)
                log_file.write(file_log + '\n')
        print("===================================================================================================")


def clean_filename(filename, c, no, u, uc):
    """Clean the file name"""

    # Delete number prefix, e.g., 232GANA-334-C.mp4 -> GANA-334-C.mp4
    filename = re.sub(r"^\d+", "", filename)

    # Delete [], e.g., [233.com]SSNI-334-C.mp4 -> SSNI-334-C.mp4
    filename = re.sub(r"^\[.*?\]", "", filename)

    # Capture the CD number if present, e.g., SSNI-888-CD2.mp4 -> CD2
    cd_number_match = re.search(r"(cd\d+)", filename, re.IGNORECASE)
    cd_number = cd_number_match.group(1) if cd_number_match else ''

    # Capture the CD number if present, e.g., SSNI-888-CD2.mp4 -> CD2
    cd_number_match = re.search(r"(cd\d+)", filename, re.IGNORECASE)
    cd_number = cd_number_match.group(1) if cd_number_match else ''

    # Add "-", e.g., SSNI334C.mp4 -> SSNI-334-C.mp4
    if re.match(r"[A-Za-z]+\d+C\.", filename):
        filename = re.sub(r"([A-Za-z]+)(\d+)(C\.)", r"\1-\2-\3", filename)
    elif re.match(r"[A-Za-z]+\d+-C\.", filename):
        filename = re.sub(r"([A-Za-z]+)(\d+)-C\.", r"\1-\2-C.", filename)
    elif re.match(r"[A-Za-z]+\d\.", filename):
        filename = re.sub(r"([A-Za-z]+)(\d+)", r"\1-\2", filename)

    # Delete all characters after the number part
    filename = re.sub(r'(\d+).*?(?=\.[^.]+$)', r'\1', filename)

    # Append the CD number if present
    if cd_number:
        filename_base, filename_extension = os.path.splitext(filename)
        filename = f"{filename_base}-{cd_number}{filename_extension}"

    # Append the CD number if present
    if cd_number:
        filename_base, filename_extension = os.path.splitext(filename)
        filename = f"{filename_base}-{cd_number}{filename_extension}"

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