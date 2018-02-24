import hashlib


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

def wages_convert(value):
    """
    Item输入处理器，将字符K转为000，并返回整数
    """
    if isinstance(value, list):
        value = value[0]

    if "K" or "k" in value:
        value = value.replace("K", "000")
        value = value.replace("k", "000")
        return [value]
    else:
        return value

def remov_tag(value):
    """
    Item输入处理器，将字符串中普通符号与空格去除
    """
    whitespace = ' \t\n\r\v\f'
    punctuation = r"""!"#$%&'()*+,./:;<=>?@[\]^_`{|}~"""

    if isinstance(value, list):
        value = value[0]
    for i in punctuation + whitespace:
        if i in value:
            value = value.replace(i, "")
    return [value]

def max_num(value):
    """
    Item输入处理器，返回大的数值
    """
    if isinstance(value, list):
        value = value[0]
    if "以下" in value:
        value = value.replace('经验', '')
        value = value.replace('年', '')
        value = value.replace('及', '')
        value = value.replace('以下', '')
        return [int(value)]
    if "-" in value:
        value = value.replace('经验', '')
        value = value.replace('年', '')
        value = value.split('-')
        return [max(int(value[0]), int(value[1]))]
    else:
        return [0]

def min_num(value):
    """
    Item输入处理器，返回小的数值
    """
    if isinstance(value, list):
        value = value[0]
    if "以上" in value:
        value = value.replace('经验', '')
        value = value.replace('年', '')
        value = value.replace('及', '')
        value = value.replace('以上', '')
        return [int(value)]
    if "-" in value:
        value = value.replace('经验', '')
        value = value.replace('年', '')
        value = value.split('-')
        return [min(int(value[0]), int(value[1]))]
    else:
        return [0]

def filter_company(value):
    """
    过滤公司部门中的招聘
    """
    if isinstance(value, list):
        value = value[0]
    value = value.replace('招聘', '')
    return [value]


def filter_education_requirements(value):
    """
    过滤学历要求中的多余字符
    """
    if isinstance(value, list):
        value = value[0]
    value = value.replace('及以上', '')
    return [value]


def filter_addrs(value):
    """
    过滤地址中多余字符
    """
    if isinstance(value, list):
        value = "".join(value)
        value = value.replace('查看地图', '')
        return [value]
    else:
        return [value]