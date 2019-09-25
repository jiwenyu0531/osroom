import time
import datetime
import os
from apps.app import mdbs
from bson import ObjectId
from apps.modules.translations.process.translator import translate_sentense, translate_word
from apscheduler.schedulers.background import BackgroundScheduler
import nltk
from nltk.corpus import stopwords


def do_translation():
    print("start to load post and do translation")
    max_loop = 100
    for i in range(max_loop):
        # read the queue
        condition = {"status": "todo", "post_time": 1}
        to_do = mdbs["web"].db.to_translate_queue.find_one(condition)
        if not to_do:
            return

        # update it to doing, this is to avoid duplicate processing
        id = to_do.get("_id")
        update_condition = {"_id": id, "status": "todo"}
        update_status = {"status": "doing"}
        doing = mdbs["web"].db.to_translate_queue.update_one(update_condition, {'$set': update_status})

        if doing.modified_count != 1:
            continue

        # translate
        post = mdbs["web"].db.post.find_one({"_id": ObjectId(to_do.get("post_id"))})
        if post:
            subtitle_content = post.get("subtitle_content")
            translation_content = list()
            sentence_set = set()
            sentence_list = list()
            vocabulary_set = set()
            vocabulary_list = list()
            # 去掉标点符号,     # all to lower case
            english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']
            # 去掉停用词
            stops = set(stopwords.words("english"))
            for subtitle in subtitle_content:
                if subtitle.get("text"):
                    text = subtitle.get("text").strip()
                    trans_text = translate_sentense(text)
                    translation_content.append({"index": subtitle.get("index"), "text": trans_text})
                    # extract sentence
                    sents = nltk.sent_tokenize(text)
                    for sent in sents:
                        if sent in sentence_set:
                            continue
                        sent_trans = translate_sentense(sent)
                        sentence_list.append({"input": sent,
                                              "output": sent_trans})
                        words = nltk.word_tokenize(sent)
                        words = [word.strip() for word in words if
                                 word.strip() and word.strip() not in english_punctuations]
                        for w in words:
                            if w in vocabulary_set or w in stops:
                                continue
                            vocabulary_set.add(w)
                            w_trans = translate_sentense(w)
                            vocabulary_list.append({"input": w,
                                                    "output": w_trans})

            # saving the content
            update_insert_content_trans(translation_content, post.get("_id"))
            # saving
            update_insert_sentence_trans(sentence_list)
            update_insert_vocabulary_trans(vocabulary_list)


def update_insert_sentence_trans(sentence_list):
    for s in sentence_list:
        current_s = mdbs["web"].db.sentence.find_one({"input": s.get("input")})
        if current_s:
            if len(current_s.get("output").strip()):
                # 存在，但是并没内容，做更新
                mdbs["web"].db.sentence.update_one({"_id": current_s.get("_id")},
                                               {'$set': {"output": s.get("output")}})
            continue
        # insert a new one
        mdbs["web"].db.sentence.insert_one(s)


def update_insert_vocabulary_trans(vocabulary_list):
    for v in vocabulary_list:
        current_v = mdbs["web"].db.vocabulary.find_one({"input": v.get("input")})
        if current_v:
            if len(current_v.get("output").strip()):
                # 存在，但是并没内容，做更新
                mdbs["web"].db.vocabulary.update_one({"_id": current_v.get("_id")},
                                                     {'$set': {"output": v.get("output")}})
            continue
        # insert a new one
        mdbs["web"].db.vocabulary.insert_one(v)


def update_insert_content_trans(translation_content, post_id):
    # check if have existing translation, if yes, update it
    current_trans = mdbs["web"].db.translation.find_one({"target_id": ObjectId(post_id),
                                                         "from_lang": "en",
                                                         "to_lang": "zh",
                                                         "user_name": "AI"})
    if current_trans:
        # update it
        mdbs["web"].db.translation.update_one({"_id": current_trans.get("_id")},
                                              {'$set': {"content": translation_content,
                                                        "issue_time": time.time()}},
                                              upsert=True)
        return

    translate = {}
    translate["user_name"] = "AI"
    translate["issue_time"] = time.time()
    translate["content"] = translation_content
    translate["from_lang"] = "en"
    translate["to_lang"] = "zh"

    mdbs["web"].db.translation.insert_one(translate)


def start_schedule(interval=10):
    scheduler = BackgroundScheduler()
    scheduler.add_job(do_translation, 'interval', seconds=interval)
    scheduler.start()
    print("do_translation task scheduled has been started.")
