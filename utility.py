import re

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
    # (.*?)?[-_]?           匹配文件名中间可能存在的多余字符串，可能是垃圾讯息或表示cd的信息
    # ([a-zA-Z]+)?[-_]?     匹配属性后缀
    # (.*?)?[-_]?           匹配文件名中间可能存在的多余字符串，可能是垃圾讯息或表示cd的信息
    # (cd\d+)?[-_]?         匹配"cd"字符串+一个数字，未使用
    pattern = r'(\d{3,3})?[-_]?([a-zA-Z]+)[-_]?(\d{2,4})[-_]?(cd\d{1,1})?[-_]?([a-zA-Z]+)?[-_]?(cd\d{1,1})?[-_]?(\.\w+)$'

    match = re.match(pattern, filename)

    if not match:
        raise ValueError(f"文件名 '{filename}' 不匹配预期的格式")

    parts = list(match.groups())
    '''
    prefix_number = parts[0]
    prefix = parts[1]
    number = parts[2]
    miscan1 = parts[3]
    postfix = parts[4]
    miscan2 = parts[5]
    file_ext = parts[6]
    '''

    # 检查数字部分长度，如果少于3，则打印警告
    if len(parts[2]) < 3:
        print("警告: 番号数字部分小于三个数字")

    return parts

def modify_filename(parts, postfix=''):
    '''
    修改文件名，使其符合规范，消除可能的垃圾讯息
    :param parts: returned from function parse_filename(), including all parts from a full filename
    :param postfix: the postfix of jav, can be c(with subtitle), u(uncensored), uc(uncensored with subtitle), None(no subtitle)
    :return: modified filename
    '''
    prefix_number = parts[0]
    prefix = parts[1]
    number = parts[2]
    miscan1 = parts[3]
    postfix = parts[4]
    miscan2 = parts[5]
    file_ext = parts[6]





filename = "example_1234_c.mp4"
#print(parse_filename(filename))  # ['example', '1234', 'c', '.mp4']
print(clean_filename(filename))
filename = "example_1234_c.mp4"
print(parse_filename(filename))  # ['SSNI', '469', 'C', '.mp4']
