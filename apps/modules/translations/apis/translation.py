# -*-coding:utf-8-*-
from flask import request
from apps.core.flask.login_manager import osr_login_required
from apps.configs.sys_config import METHOD_WARNING
from apps.core.blueprint import api
from apps.core.flask.permission import permission_required
from apps.core.flask.response import response_format
from apps.modules.translations.process.translation import translations, translation_issue, translation_delete, \
    translation_like

__author__ = 'jiwen'


@api.route('/translations', methods=['GET'])
@permission_required(use_default=False)
def api_get_translation():
    """
    GET:
        获取文章的翻译
        target_id:<str>, 目标id,比如文章post id
        target_type:<str>, 目标类型,比如文章就是"post"
        status:<str>,"is_issued"（正常发布） or "not_audit"（等待审核） or "unqualified"（未通过审核） or "user_remove"(用户删除的)

        sort:<array>,排序, 1表示升序, -1表示降序.如:
            按时间降序 [{"issue_time":-1}]
            按时间升序 [{"issue_time": 1}]
            先后按赞(like)数降序, 评论数降序,pv降序, 发布时间降序
            [{"like": -1},{"issue_time": -1}]
            默认时按时间降序, 也可以用其他字段排序

        page:<int>,第几页，默认第1页
        pre:<int>, 每页查询多少条, 默认是config.py配制文件中配制的数量
        :return:

    """
    data = translations()
    return response_format(data)


@api.route('/translations', methods=['POST', 'PUT', 'PATCH', 'DELETE'])
@permission_required(use_default=False)
def api_translation_op():
    """
    POST:
        发布一个翻译
        target_id:<str>, 目标id,比如文章post id
        target_type:<str>, 目标类型,比如文章就是"post"

        user_id:<str>, 翻译者的id.
        language:<str>, 翻译的语言

        content:<str>, 内容(比如:富文本的html内容),将会保存到数据库中

        如果是游客评论,则需要以下两个参数(需要再后台配置中开启游客评论开关):
        username:<str>, 游客昵称
        email:<str>,游客邮箱
        :return:

    DELETE:
        评论删除
        ids:<array>, translations ids
    """
    if request.c_method == "POST":
        data = translation_issue()

    elif request.c_method == "DELETE":
        data = translation_delete()

    else:
        data = {"msg_type": "w", "msg": METHOD_WARNING, "custom_status": 405}
    return response_format(data)


@api.route('/translations/like', methods=['PUT'])
@osr_login_required
@permission_required(use_default=False)
def api_translation_like():
    """
    PUT:
        给翻译点赞
        id:<str>
    :return:
    """
    data = translation_like()
    return response_format(data)
