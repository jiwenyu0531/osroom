import os
from os import path
from PIL import Image
import numpy as np
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from apps.configs.sys_config import STATIC_PATH, APPS_PATH
from apps.core.utils.get_config import get_config


def get_frequency_for_txt(sentence):
    text_list = nltk.word_tokenize(sentence)
    # 去掉标点符号,     # all to lower case
    english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']

    text_list = [str.lower(word) for word in text_list if word not in english_punctuations]
    # 去掉停用词
    stops = set(stopwords.words("english"))
    excluded_abbr = ["'ll", "'s", "'m", "'re"]
    for ex in excluded_abbr:
        stops.add(ex)
    text_list = [word for word in text_list if word not in stops]

    freq_dist = nltk.FreqDist(text_list)
    return freq_dist


def word_cloud_gen_per_frequency(text_freq, save_name, mask_img=None):
    if mask_img:
        alice_mask = np.array(Image.open(mask_img))
        wc = WordCloud(background_color="white", max_words=1000, mask=alice_mask)
    else:
        wc = WordCloud(background_color="white", max_words=1000)

    # generate word cloud
    wc.generate_from_frequencies(text_freq)

    # saving to file
    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    # 文件保存的绝对路径
    save_file_path = "{}/{}/{}".format(
        STATIC_PATH, get_config(
            "upload", "SAVE_DIR"), save_name).replace(
        "//", "/")
    wc.to_file(save_file_path)

    # return the file path relative path
    return save_file_path.replace(APPS_PATH, '')


