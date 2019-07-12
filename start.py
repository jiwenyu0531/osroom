#!/usr/bin/env python3
# -*-coding:utf-8-*-
import sys
from signal import signal, SIGCHLD, SIG_IGN
from pymongo.errors import OperationFailure
from apps.configs.config import CONFIG
from apps.configs.db_config import DB_CONFIG
from apps.core.db.config_mdb import DatabaseConfig
from apps.core.utils.sys_tool import update_pylib, add_user as add_user_process

__author__ = 'all.woo'

"""
manage
"""

# 网站还未启动的时候, 临时连接数据库, 更新collection

print("\033[1;36m[OSROOM] Staring...\033[0m")
from apps.core.utils.update_sys_data import update_mdb_collections, init_datas, compatible_processing, \
    update_mdbcolls_json_file
from apps.core.db.mongodb import PyMongo
print(" * Check or update the database collection")
database = DatabaseConfig()
mdbs = {}
for k, mdb_acc in DB_CONFIG["mongodb"].items():
    mdbs[k] = PyMongo()

db_init = 2
while db_init:
    try:
        for name, mdb in mdbs.items():
            if name not in ["sys", "user", "web"]:
                print(" *[Error] 由v1.x.x更新到v2.x.x需要请更新你的数据库配置文件apps/configs/db_config.py\n"
                      "  请参考同目录下的db_config_sample.py")
                sys.exit()
            mdb.init_app(config_prefix=name.upper(),
                         db_config=database.__dict__["{}_URI".format(name.upper())])
    except OperationFailure as e:
        print("\n[Mongodb] *{}".format(e))
        print("Mongodb validation failure, the user name,"
              " password mistake or database configuration errors.\n"
              "Tip: to open database authentication configuration")
        sys.exit(-1)
    if db_init == 2:
        update_mdb_collections(mdbs=mdbs)
    db_init -= 1

# 更新配置文件
from apps.core.flask.update_config_file import update_config_file
print(" * Update and sync config.py")
r = update_config_file(mdbs=mdbs)
if not r:
    print("[Error] Update profile error, check log sys_start.log")
    sys.exit(-1)
del CONFIG["py_venv"]

compatible_processing(mdbs=mdbs)
init_datas(mdbs=mdbs)
for mdb in mdbs.values():
    mdb.close()

# 启动网站
from flask_script import Manager
from apps.app import app
from apps.core.flask.module_import import module_import
from apps.init_core_module import init_core_module
from apps.configs.sys_config import MODULES
from apps.sys_startup_info import start_info

start_info()
init_core_module(app)
module_import(MODULES)
manager = Manager(app)
if "--debug" not in sys.argv and "-D" not in sys.argv:
    print(" * Signal:(SIGCHLD, SIG_IGN).Prevent child processes from becoming [Defunct processes]."
          "(Do not need to comment out)")
    signal(SIGCHLD, SIG_IGN)


@manager.command
def add_user():
    update_mdb_collections(mdbs=mdbs)
    init_datas(mdbs=mdbs)
    add_user_process(mdbs=mdbs)


@manager.command
def dbcoll_to_file():
    """
    更新mdb collections到json文件中
    :return:
    """
    update_mdbcolls_json_file(mdbs=mdbs)


if __name__ == '__main__':
    """
    使用Flask 自带 server启动网站
    """
    print(" * Use the Web service that comes with Flask")
    if "--debug" not in sys.argv and "-D" not in sys.argv:
        # 更新python第三方类库
        print(" * Check or update Python third-party libraries")
        #update_pylib(input_venv_path=False)
    else:
        print(" * Using --debug, the system will not check Python dependencies")

    manager.run()
