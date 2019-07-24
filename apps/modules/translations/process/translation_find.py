# -*-coding:utf-8-*-
from copy import deepcopy
from flask_babel import gettext
from flask_login import current_user
from apps.utils.format.obj_format import objid_to_str
from apps.utils.format.time_format import time_to_utcdate
from apps.utils.paging.paging import datas_paging
from apps.app import mdbs
from apps.core.utils.get_config import get_config

__author__ = 'Allen Woo'


def find_translations(
        query_conditions={},
        page=1,
        pre=10,
        sort=None,
        keyword="",
        status="is_issued",
        *args,
        **kwargs):

    data = {}
    if pre > get_config("translation", "NUM_PAGE_MAX"):
        data = {"msg": gettext('The "pre" must not exceed the maximum amount'),
                "msg_type": "e", "custom_status": 400}
        return data

    query_conditions = deepcopy(query_conditions)

    if status == "not_audit":
        query_conditions['issued'] = 1
        query_conditions['is_delete'] = 0
        # 没有审核, 而且默认评分涉嫌违规的
        query_conditions['audited'] = 0
        query_conditions['audit_score'] = {
            "$gte": get_config(
                "content_inspection",
                "ALLEGED_ILLEGAL_SCORE")}

    elif status == "unqualified":
        query_conditions['issued'] = 1
        query_conditions['is_delete'] = 0
        query_conditions['audited'] = 1
        query_conditions['audit_score'] = {
            "$gte": get_config(
                "content_inspection",
                "ALLEGED_ILLEGAL_SCORE")}

    elif status == "user_remove":
        query_conditions['is_delete'] = {"$in": [1, 2]}

    else:
        query_conditions['issued'] = 1
        query_conditions['is_delete'] = 0
        query_conditions['audit_score'] = {
            "$lt": get_config(
                "content_inspection",
                "ALLEGED_ILLEGAL_SCORE")}

    if keyword:
        keyword = {"$regex": keyword, "$options": "$i"}
        query_conditions["content"] = keyword

    cs = mdbs["web"].db.translation.find(query_conditions)
    data_cnt = cs.count(True)

    # sort
    if sort:

        for i, srt in enumerate(sort):
            sort[i] = (list(srt.keys())[0], list(srt.values())[0])

    else:
        sort = [("issue_time", -1)]

    translations = list(cs.sort(sort).skip(pre * (page - 1)).limit(pre))
    # translations = recursive_find_translation(translations)

    data["translations"] = datas_paging(
        pre=pre,
        page_num=page,
        data_cnt=data_cnt,
        datas=translations)
    return data

'''
def recursive_find_translation(translations):

    for translation in translations:
        translation = objid_to_str(
            translation, [
                "_id", "user_id", "audit_user_id", ""])
        translation["date"] = time_to_utcdate(
            time_stamp=translation["issue_time"],
            tformat="%Y-%m-%d %H:%M")
        if current_user.is_authenticated:
            r = mdbs["user"].db.user_like.find_one(
                {"user_id": current_user.str_id, "type": "translations", "values": translation["_id"]})
            if r:
                translation["like_it_already"] = True
        # 评论下面的所有回复
        query_conditions = {}
        query_conditions['issued'] = 1
        query_conditions['is_delete'] = 0
        query_conditions['audit_score'] = {
            "$lt": get_config(
                "content_inspection",
                "ALLEGED_ILLEGAL_SCORE")}
        # query_conditions["reply_id"] = translation["_id"]
        reply_translations = mdbs["web"].db.translation.find(
            query_conditions).sort([("issue_time", -1)])
        if reply_translations.count(True):
            translation["reply"] = objid_to_str(
                list(reply_translations), [
                    "_id", "user_id", "audit_user_id"])
            translation["reply"] = recursive_find_translation(translation["reply"])

    return translations
'''

