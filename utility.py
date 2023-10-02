import re
import threading


class InvalidFilenameError(Exception):
    pass


def clean_filename(filename):
    '''
    :param filename: Input filename from main
    :return: cleaned_filename: Filename with removed head and tail ads
    '''
    # 分离文件名和拓展名
    body, extension = re.match(r'(.*?)(\.\w+)$', filename).groups()

    # 检查是否存在 "japlib.top" 类型的前缀
    domain_pattern = r'^[a-zA-Z0-9\-_]+\.([a-zA-Z0-9]+)[-_]'
    domain_match = re.match(domain_pattern, body)
    if domain_match:
        body = body[len(domain_match.group(0)):]
    # 清理开头的无用字符
    body = re.sub(r'^[^a-zA-Z0-9-_]+', '', body)

    # 清理结尾的无用字符
    body = re.sub(r'[^a-zA-Z0-9-_]+', '', body)

    # 重新组合文件名和拓展名
    cleaned_filename = f'{body}{extension}'
    return cleaned_filename


def parse_filename(filename):
    # 正则表达式分解为：
    # (\d{3,3})?[-_]?       匹配前缀前面的数字，强制限制为3，可选，可选的"-"或"_"连接符
    # ([a-zA-Z]+)[-_]?      匹配前缀，只包含字母
    # (\d{2,4})[-_]?        匹配2到4个数字
    # ([a-zA-Z]+)?[-_]?     匹配第一个属性后缀
    # ([a-zA-Z]+)?[-_]?     匹配第二个属性后缀
    # (.*?)?[-_]?           匹配文件名中间可能存在的多余字符串，可能是垃圾讯息或表示cd的信息
    # (cd\d+)?[-_]?         匹配"cd"字符串+一个数字，未使用
    pattern = \
        (r'(\d{3,3})?[-_]?'  # [0],前缀前面的数字
         r'([a-zA-Z]+)[-_]?'  # [1],前缀
         r'(\d{2,4})[-_]?'  # [2],2到4个数字
         r'([a-zA-Z]+)?[-_]?'  # [3],第一个属性后缀
         r'([a-zA-Z]+)?[-_]?'  # [4],第二个属性后缀
         r'(cd\d{1,1})?[-_]?'  # [5],"cd"字符串
         r'(\.\w+)$')  # [6],文件拓展名

    match = re.match(pattern, filename)

    if not match:
        raise ValueError(f"文件名 '{filename}' 不匹配预期的格式")

    parts = list(match.groups())
    '''
    prefix_number  = parts[0]
    prefix         = parts[1]
    number         = parts[2]
    postfix1       = parts[3]
    postfix2       = parts[4]
    cd             = parts[5]
    file_ext       = parts[6]
    '''

    # 检查数字部分长度，如果少于3，则打印警告
    if len(parts[2]) < 3:
        print("警告: 番号数字部分小于三个数字")

    return parts


def modify_filename(parts, postfix='', prefix_num=True):
    """
    修改文件名，使其符合规范，消除可能的垃圾讯息
    :param parts: returned from function parse_filename(), including all parts from a full filename
    :param postfix: the postfix of jav, can be c(with subtitle), u(uncensored), uc(uncensored with subtitle), None(no subtitle)
    :param prefix_num: Remain prefix number or not
    :return: result: modified filename
    """
    postfix = postfix.lower()
    if postfix != 'c' or postfix != 'no' or postfix != 'u' or postfix != 'uc':
        raise AttributeError("The postfix argument is invalid!")
    prefix_number = parts[0]
    prefix = parts[1]
    number = parts[2]
    postfix1 = parts[3]
    postfix2 = parts[4]
    cd = parts[5]
    file_ext = parts[6]
    modified_filename = []

    # Add or delete prefix number
    if prefix_num:
        modified_filename = [prefix_number, prefix, number]
    else:
        modified_filename = [prefix, number]

    def handleException(pos1, pos2):
        modified_filename.append(pos1)
        modified_filename.append(pos2)

    # Add postfix according to different postfix requirement
    try:
        if postfix == 'c':
            if postfix1.lower() == postfix:
                modified_filename.append(postfix1.upper())
                if postfix2:
                    modified_filename.append(postfix2)
            elif postfix2.lower() == postfix:
                modified_filename.append(postfix2.upper())
                if postfix1:
                    modified_filename.append(postfix1)
            else:
                handleException(postfix1, postfix2)
                postfix = 'C'
                raise InvalidFilenameError(
                    f"The filename has no postfix that match the rules, the file is: {modified_filename}.")
        elif postfix == 'no' or not postfix:
            if postfix1 and postfix2:
                handleException(postfix1, postfix2)
                print(f"The filename has unexpected postfix, which are: {[postfix1, postfix2]}.")
        elif postfix == 'u':
            if postfix1.lower() == postfix or postfix1.lower() == 'hack':
                handleException('hack', postfix2)
            elif postfix2.lower() == postfix or postfix2.lower() == 'hack':
                handleException(postfix1, 'hack')
            else:
                handleException(postfix1, postfix2)
                postfix = 'hack'
                raise InvalidFilenameError(
                    f"The filename has no postfix that match the rules, the file is: {modified_filename}.")
        elif postfix == 'uc':
            if postfix1.lower() == 'uc' or postfix2.lower() == 'uc':
                handleException('hack', 'C')
            elif postfix1.lower() in ['u', 'hack']:
                if postfix2.lower() == 'c':
                    handleException('hack', 'C')
                else:
                    handleException('hack', postfix2)
                    postfix = 'C'
                    raise InvalidFilenameError(
                        f"The filename has no postfix that match the rules, the file is: {modified_filename}.")
            elif postfix1.lower() == 'c':
                if postfix2.lower() in ['u', 'hack']:
                    handleException('hack', 'C')
                else:
                    handleException(postfix1, 'C')
                    postfix = 'hack'
                    raise InvalidFilenameError(
                        f"The filename has no postfix that match the rules, the file is: {modified_filename}.")
            elif postfix2 in ['u', 'hack']:
                if postfix1.lower() == 'c':
                    handleException('hack', 'C')
                else:
                    handleException(postfix2, 'hack')
                    postfix = 'C'
                    raise InvalidFilenameError(
                        f"The filename has no postfix that match the rules, the file is: {modified_filename}.")
            elif postfix2.lower() == 'c':
                if postfix1.lower() in ['u', 'hack']:
                    handleException('hack', 'C')
                else:
                    handleException(postfix1, 'C')
                    postfix = 'hack'
                    raise InvalidFilenameError(
                        f"The filename has no postfix that match the rules, the file is: {modified_filename}.")
            else:
                handleException(postfix1, postfix2)
                postfix = ['hack', 'C']
                raise InvalidFilenameError(
                    f"The filename has no postfix that match the rules, the file is: {modified_filename}.")
    except InvalidFilenameError as e:
        print(f"Warning: {e}")
        while True:
            user_input = input(f"Do you want add postfix \"{postfix}\" to the filename? (Y/n): ").lower()
            if not user_input or user_input in ['y', '']:
                modified_filename.append(postfix)
                break
            elif user_input.lower() == 'n':
                print("Stopping the process.")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n', or press ENTER for 'y'.")

    if prefix_num:
        first_item = str(modified_filename[0])
        remaining_items = '-'.join(str(item) for item in modified_filename[1:])
        result = f"{first_item}{remaining_items}"
    else:
        result = '-'.join(str(item) for item in modified_filename)

    if cd:
        result += cd
    result += file_ext

    return result


filename = "ssni-234-hack-c-cd1.mp4"
print(parse_filename(filename))  # ['example', '1234', 'c', '.mp4']
print(clean_filename(filename))
filename = "example_1234_c.mp4"
print(parse_filename(filename))  # ['SSNI', '469', 'C', '.mp4']
