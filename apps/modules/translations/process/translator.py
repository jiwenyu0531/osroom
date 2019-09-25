from apps.app import cache, mdbs


def translate_sentense(sentense, to_language):
    s, r = find_local_history_sentense(sentense, to_language)
    if s:
        return r

    s, r, b = forwarding_translate_sentense(sentense, to_language)

    if s:
        # add this to local history
        new_sentense = {"input": sentense,
                        "to_language": to_language,
                        "output": r,
                        "source": b,
                        "frequency": 0}
        mdbs["web"].db.sentence.insert_one(new_sentense)
        return r
    # 如果没有成功怎么办？ 如，网络异常等查询不到结果， 希望不要cache未成功的查询
    return ''


def translate_word(word, to_language):
    # read cache first
    # then read local hestory
    # then forward to baidu or other online translation tools
    pass


@cache.cached(timeout=3600, key_base64=False, db_type="redis")
def find_local_history_sentense(sensense, to_language):
    # increase the frequency
    pass


@cache.cached(timeout=3600, key_base64=False, db_type="redis")
def find_local_history_word(word, to_language):
    pass


def forwarding_translate_sentense(sentense, to_language):
    pass


def forwarding_translate_word(world, to_language):
    pass
