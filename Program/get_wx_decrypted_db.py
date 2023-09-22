# -*- coding: utf-8 -*-#

import os
import re
import shutil
import sqlite3
from decrypt import decrypt


# ToDo: 更改为你自己的wechat files路径
MSG_DIR = '/home/user/Documents/WeChat Files'


# 开始获取微信数据库
def get_wechat_db(wechatUserAccount):
    user_dirs = {}  # wx用户目录
    files = os.listdir(MSG_DIR)
    for file_name in files:
        if file_name == "All Users" or file_name == "Applet" or file_name == "WMP":
            continue
        if not os.path.exists(os.path.join(os.path.join(MSG_DIR, file_name), 'account_'+wechatUserAccount)):
            continue
        user_dirs[file_name] = os.path.join(MSG_DIR, file_name)

    # 获取数据库路径
    for user, user_dir in user_dirs.items():
        Media_p = []
        Micro_p = []
        FTS_p = []
        Sns_p = []
        Msg = []
        Emotion_p = []
        for root, dirs, files in os.walk(user_dir):
            for file_name in files:
                if re.match(r".*MediaMSG.*\.db$", file_name):
                    src_path = os.path.join(root, file_name)
                    Media_p.append(src_path)
                elif re.match(r".*MicroMsg.*\.db$", file_name):
                    src_path = os.path.join(root, file_name)
                    Micro_p.append(src_path)
                elif re.match(r".*FTSMSG.*\.db$", file_name):
                    src_path = os.path.join(root, file_name)
                    FTS_p.append(src_path)
                elif re.match(r".*MSG.*\.db$", file_name):
                    src_path = os.path.join(root, file_name)
                    Msg.append(src_path)
                elif re.match(r".*Sns.*\.db$", file_name):
                    src_path = os.path.join(root, file_name)
                    Sns_p.append(src_path)
                elif re.match(r".*Emotion.*\.db$", file_name):
                    src_path = os.path.join(root, file_name)
                    Emotion_p.append(src_path)
        Media_p.sort()
        Msg.sort()
        Micro_p.sort()
        # FTS_p.sort()
        user_dirs[user] = {"MicroMsg": Micro_p, "Msg": Msg, "MediaMSG": Media_p, "Sns": Sns_p, "Emotion": Emotion_p}
    return user_dirs


# 解密所有数据库 paths（文件） 到 decrypted_path（目录）
def all_decrypt(keys, paths, decrypted_path):
    decrypted_paths = []

    for key in keys:
        for path in paths:

            name = os.path.basename(path)  # 文件名
            dtp = os.path.join(decrypted_path, name)  # 解密后的路径
            if not decrypt(key, path, dtp):
                break
            decrypted_paths.append(dtp)
        else:  # for循环正常结束，没有break
            break  # 跳出while循环
    else:
        return False  # while循环正常结束，没有break 解密失败
    return decrypted_paths


def merge_copy_msg_db(db_path, save_path):
    for i in db_path:
        if not os.path.exists(i):
            raise FileNotFoundError("目录不存在")
        shutil.move(i, save_path)


# 合并相同名称的数据库
def merge_msg_db(db_path, save_path, CreateTime):  # CreateTime: 从这个时间开始的消息 10位时间戳

    merged_conn = sqlite3.connect(save_path)
    merged_cursor = merged_conn.cursor()

    for db_file in db_path:
        c_tabels = merged_cursor.execute(
            "select tbl_name from sqlite_master where  type='table' and tbl_name!='sqlite_sequence'")
        tabels_all = c_tabels.fetchall()  # 所有表名
        tabels_all = [row[0] for row in tabels_all]

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # 创建表
        if len(tabels_all) < 4:
            cursor.execute(
                "select tbl_name,sql from sqlite_master where type='table' and tbl_name!='sqlite_sequence'")
            c_part = cursor.fetchall()

            for tbl_name, sql in c_part:
                if tbl_name in tabels_all:
                    continue
                try:
                    merged_cursor.execute(sql)
                    tabels_all.append(tbl_name)
                except Exception as e:
                    print(str(e))
                    raise e
                merged_conn.commit()

        # 写入数据
        for tbl_name in tabels_all:
            if tbl_name == "MSG":
                MsgSvrIDs = merged_cursor.execute(
                    "select MsgSvrID from MSG where CreateTime> {} and MsgSvrID!=0".format(CreateTime)).fetchall()

                cursor.execute("PRAGMA table_info({0})".format(tbl_name))
                columns = cursor.fetchall()
                columns = [column[1] for column in columns[1:]]

                ex_sql = "select {} from {} where CreateTime>{} and MsgSvrID not in ({})".format(
                    ','.join(columns), tbl_name, CreateTime, ','.join([str(MsgSvrID[0]) for MsgSvrID in MsgSvrIDs]))
                cursor.execute(ex_sql)

                insert_sql = "INSERT INTO {} ({}) VALUES ({})".format(
                    tbl_name, ','.join(columns), ','.join(['?' for _ in range(len(columns))]))
                try:
                    merged_cursor.executemany(insert_sql, cursor.fetchall())
                except Exception as e:
                    print(str(e))
                    raise e
                merged_conn.commit()
            else:
                ex_sql = "select * from {}".format(tbl_name)
                cursor.execute(ex_sql)

                for r in cursor.fetchall():
                    cursor.execute("PRAGMA table_info({})".format(tbl_name))
                    columns = cursor.fetchall()
                    if len(columns) > 1:
                        columns = [column[1] for column in columns[1:]]
                        values = r[1:]
                    else:
                        columns = [columns[0][1]]
                        values = [r[0]]

                        query_1 = "select * from " + tbl_name + " where " + columns[0] + "=?"  # 查询语句 用于判断是否存在
                        c2 = merged_cursor.execute(query_1, values)
                        if len(c2.fetchall()) > 0:  # 已存在
                            continue
                    query = "INSERT INTO " + tbl_name + " (" + ",".join(columns) + ") VALUES (" + ",".join(
                        ["?" for _ in range(len(values))]) + ")"

                    try:
                        merged_cursor.execute(query, values)
                    except Exception as e:
                        print(str(e))
                        raise e
                merged_conn.commit()

        conn.close()
    # sql = '''delete from MSG where localId in (SELECT localId from MSG
    #    where MsgSvrID != 0  and MsgSvrID in (select MsgSvrID  from MSG
    #                       where MsgSvrID != 0 GROUP BY MsgSvrID  HAVING COUNT(*) > 1)
    #      and localId not in (select min(localId)  from MSG
    #                          where MsgSvrID != 0  GROUP BY MsgSvrID HAVING COUNT(*) > 1))'''
    # c = merged_cursor.execute(sql)
    merged_conn.commit()
    merged_conn.close()
    return save_path


def merge_media_msg_db(db_path, save_path):
    merged_conn = sqlite3.connect(save_path)
    merged_cursor = merged_conn.cursor()

    for db_file in db_path:

        s = "select tbl_name,sql from sqlite_master where  type='table' and tbl_name!='sqlite_sequence'"
        have_tables = merged_cursor.execute(s).fetchall()
        have_tables = [row[0] for row in have_tables]

        conn_part = sqlite3.connect(db_file)
        cursor = conn_part.cursor()

        if len(have_tables) < 1:
            cursor.execute(s)
            table_part = cursor.fetchall()
            tblname, sql = table_part[0]

            sql = "CREATE TABLE Media(localId INTEGER  PRIMARY KEY AUTOINCREMENT,Key TEXT,Reserved0 INT,Buf BLOB,Reserved1 INT,Reserved2 TEXT)"
            try:
                merged_cursor.execute(sql)
                have_tables.append(tblname)
            except Exception as e:
                print(str(e))
                raise e
            merged_conn.commit()

        for tblname in have_tables:
            s = "select Reserved0 from " + tblname
            merged_cursor.execute(s)
            r0 = merged_cursor.fetchall()

            ex_sql = "select * from {} where Reserved0 not in ({})".format(tblname, ','.join([str(r[0]) for r in r0]))
            cursor.execute(ex_sql)
            data = cursor.fetchall()

            insert_sql = "INSERT INTO {} (Key,Reserved0,Buf,Reserved1,Reserved2) VALUES ({})".format(tblname, ','.join(['?' for _ in range(5)]))
            try:
                merged_cursor.executemany(insert_sql, data)
            except Exception as e:
                print(str(e))
                raise e
            merged_conn.commit()
        conn_part.close()

    merged_conn.close()
    return save_path


def startDecrypted(keys, wechatUserAccount):
    decrypted_ROOT = os.path.join(os.getcwd(), "decrypted")
    user_dirs = get_wechat_db(wechatUserAccount)
    for user, db_path in user_dirs.items():  # 遍历用户
        MicroMsgPaths = db_path["MicroMsg"]
        MsgPaths = db_path["Msg"]
        MediaMSGPaths = db_path["MediaMSG"]
        # FTSMSGPaths = db_path["FTSMSG"]
        SnsPaths = db_path["Sns"]
        EmotionPaths = db_path["Emotion"]

        decrypted_path_tmp = os.path.join(decrypted_ROOT, user, "tmp")  # 解密后的目录
        if not os.path.exists(decrypted_path_tmp):
            os.makedirs(decrypted_path_tmp)

        MicroMsgDecryptPaths = all_decrypt(keys, MicroMsgPaths, decrypted_path_tmp)
        MsgDecryptPaths = all_decrypt(keys, MsgPaths, decrypted_path_tmp)
        MediaMSGDecryptPaths = all_decrypt(keys, MediaMSGPaths, decrypted_path_tmp)
        SnsDecryptPaths = all_decrypt(keys, SnsPaths, decrypted_path_tmp)
        EmotionDecryptPaths = all_decrypt(keys, EmotionPaths, decrypted_path_tmp)

        # 合并数据库
        decrypted_path = os.path.join(decrypted_ROOT, user)  # 解密后的目录

        MicroMsgDbPath = os.path.join(decrypted_path, "MicroMsg.db_dec.db")
        MsgDbPath = os.path.join(decrypted_path, "MSG0.db_dec.db")
        MediaMSGDbPath = os.path.join(decrypted_path, "MediaMSG_all.db_dec.db")
        SnsDbPath = os.path.join(decrypted_path, "Sns_all.db_dec.db")
        EmmotionDbPath = os.path.join(decrypted_path, "Emotion_all.db_dec.db")

        merge_copy_msg_db(MicroMsgDecryptPaths, MicroMsgDbPath)
        merge_msg_db(MsgDecryptPaths, MsgDbPath, 0)
        merge_media_msg_db(MediaMSGDecryptPaths, MediaMSGDbPath)
        merge_copy_msg_db(SnsDecryptPaths, SnsDbPath)
        merge_copy_msg_db(EmotionDecryptPaths, EmmotionDbPath)

        shutil.rmtree(decrypted_path_tmp)  # 删除临时文件
