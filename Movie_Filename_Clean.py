import os
import re
import sys
import time


def is_valid_file_size(file_path, size_limit):
    """Check file size limit"""
    return os.path.getsize(file_path) < size_limit


def clean_filename(filename):
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

    # Add "-C" if it is not exist, e.g., SSNI-334.mp4 -> SSNI-334-C.mp4
    if not re.search(r"-c\.(?=[^.]+$)", filename, re.I):  # re.I 是大小写不敏感标志
        filename = re.sub(r"\.(?=[^.]+$)", "-C.", filename)

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


def main(dry_run=True, folder_path=""):
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

            # 清理文件名
            # TODO: Output a txt file with the log
            cleaned_filename = clean_filename(file_name)
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
    # 创建配置解析器
    config = configparser.ConfigParser()

    # 读取config.ini文件
    config.read(c+'config.ini')

    # 如果folder_path的最后一个字符不是路径分隔符，则添加一个
    if not f.endswith('/'):
        f += '/'

    # 根据folder_path设置failed_output_folder
    failed_output_folder = f + "fail"

    # 修改source_folder值
    config['common']['source_folder'] = f

    # 修改success_output_folder值
    config['common']['success_output_folder'] = o

    # 修改failed_output_folder值
    config['common']['failed_output_folder'] = failed_output_folder

    # 将修改后的内容写回config.ini文件
    with open('./config.ini', 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process video files.')
    parser.add_argument('-s', '--source', type=str, required=True, help='Source folder path')
    parser.add_argument('-dp', '--destination', type=str, required=True, help='Success output folder path')
    parser.add_argument('-m', '--mdc', type=str, required=True, help='MDC file path')
    parser.add_argument('-d', '--dryrun', action='store_true', help='Enable dry run mode')

    args = parser.parse_args()

    # 获取目录路径
    folder_path = args.source
    success_output_path = args.destination
    mdc_path = args.mdc
    if not mdc_path.endswith('/'):
        mdc_path += '/'
    config_path = mdc_path

    # 检查输入的目录是否存在
    if not os.path.exists(folder_path):
        print("The path is not exist, exit.")
        sys.exit()

    dry_run = args.dryrun
    if dry_run:
        print("DRY RUN, will not affect the file")
    else:
        print("The program will modify these files:")

    main(True, folder_path)

    if not dry_run:
        try:
            countdown(10)
        except KeyboardInterrupt:
            print("\nOperation interrupted by user, abort.")
            sys.exit()
        main(False, folder_path)

    """ Modify the MDC configuration file """
    modify_config(config_path, folder_path, success_output_path)

    """ Run MDC """
    try:
        subprocess.run([mdc_path+'mdc'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while running mdc: {e}")
