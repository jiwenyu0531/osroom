# -*-coding:utf-8-*-
import os
import re
from apps.configs.sys_config import APPS_PATH

__author__ = "Jiwen"


def get_subtitle_content(file_path):
    file = APPS_PATH + file_path
    if not os.path.exists(file):
        return []
    with open(file, 'r') as f:
        text_lines = f.readlines()
        # 加载数据到dict 中
        return load_file_2_dict(text_lines)


def load_file_2_dict(text_lines):
    # subtitle_df = pd.DataFrame(columns=['index', 'start_time', 'end_time', 'text'])
    ret = []
    time_re = re.compile('\d+:\d+:\d+.\d+')
    i = 0
    seq = 0
    count = len(text_lines)
    while i < count:
        # locate the time line
        if len(time_re.findall(str(text_lines[i]))) == 2:
            # 获取时间标签
            time_values = time_re.findall(str(text_lines[i]))
            line = dict()
            line['index'] = seq
            line['start_time'] = time_values[0]
            line['end_time'] = time_values[1]
            text = ''
            # 内循环，添加文字内容
            while i + 1 < count and len(re.findall('^\d+\n', str(text_lines[i + 1]))) != 1:
                i = i + 1
                text = text + str(text_lines[i])

            # save it
            if time_values[0].strip() == time_values[1].strip():
                # 如果时间相等，显然这是版权的水印，应该忽略
                i = i + 1
                continue
            text = re.sub('\n', ' ', text)
            line['text'] = text.strip()
            seq = seq + 1
            ret.append(line)

        # next
        i = i + 1

    return ret
