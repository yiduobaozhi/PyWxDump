# -*- coding: utf-8 -*-#

import binascii
import json
import ctypes
import re
import psutil
from get_wx_decrypted_db import startDecrypted


def get_name(pid, base_address, n_size=100):
    # 新建空缓冲区
    array = (ctypes.c_byte * n_size)()
    # 将对应内存读取到缓冲区
    with open('/proc/{}/mem'.format(pid), 'rb+') as mem:
        mem.seek(base_address)
        mem.readinto(array)
    # 查看停止下标
    null_index = n_size
    for i in range(n_size):
        if array[i] == 0:
            null_index = i
            break
    # 将内存转为中文
    text = ctypes.string_at(ctypes.byref(array), null_index).decode('utf-8', errors='ignore')
    return text


def get_account(pid, base_address, n_size=100):
    # 新建空缓冲区
    array = (ctypes.c_byte * n_size)()
    # 将对应内存读取到缓冲区
    with open('/proc/{}/mem'.format(pid), 'rb+') as mem:
        mem.seek(base_address)
        mem.readinto(array)
    # 查看停止下标
    null_index = n_size
    for i in range(n_size):
        if array[i] == 0:
            null_index = i
            break
    # 将内存转为中文
    text = ctypes.string_at(ctypes.byref(array), null_index).decode('utf-8', errors='ignore')
    return text


def get_mobile(pid, base_address, n_size=100):
    # 新建空缓冲区
    array = (ctypes.c_byte * n_size)()
    # 将对应内存读取到缓冲区
    with open('/proc/{}/mem'.format(pid), 'rb+') as mem:
        mem.seek(base_address)
        mem.readinto(array)
    # 查看停止下标
    null_index = n_size
    for i in range(n_size):
        if array[i] == 0:
            null_index = i
            break
    # 将内存转为中文
    text = ctypes.string_at(ctypes.byref(array), null_index).decode('utf-8', errors='ignore')
    return text


def get_mail(pid, base_address, n_size=100):
    # 新建空缓冲区
    array = (ctypes.c_byte * n_size)()
    # 将对应内存读取到缓冲区
    with open('/proc/{}/mem'.format(pid), 'rb+') as mem:
        mem.seek(base_address)
        mem.readinto(array)
    # 查看停止下标
    null_index = n_size
    for i in range(n_size):
        if array[i] == 0:
            null_index = i
            break
    # 将内存转为中文
    text = ctypes.string_at(ctypes.byref(array), null_index).decode('utf-8', errors='ignore')
    return text


def get_hex(pid, base_address):
    array = ctypes.create_string_buffer(8)
    with open('/proc/{}/mem'.format(pid), 'rb+') as mem:
        mem.seek(base_address)
        mem.readinto(array)

    num = 32
    array2 = (ctypes.c_ubyte * num)()
    lp_base_address2 = (
            (int(binascii.hexlify(array[3]), 16) << 24) +
            (int(binascii.hexlify(array[2]), 16) << 16) +
            (int(binascii.hexlify(array[1]), 16) << 8) +
            int(binascii.hexlify(array[0]), 16)
    )
    with open('/proc/{}/mem'.format(pid), 'rb+') as mem:
        mem.seek(lp_base_address2)
        mem.readinto(array2)
    hex_string = binascii.hexlify(bytes(array2))
    return hex_string.decode('utf-8')


def get_file_version(file_path):
    pattern = r"\[(.*?)\]"
    result = re.search(pattern, file_path)
    if result:
        content = result.group(1)
        return content

# def get_wx_id(h_process, lp_base_address):


def read_info(version_list):
    support_list = None
    wechat_process = None

    rd = []

    for process in psutil.process_iter(['name', 'exe', 'pid', 'cmdline']):
        if process.name() == 'WeChat.exe':
            tmp_rd = {}
            wechat_process = process
            tmp_rd['pid'] = wechat_process.pid
            # print("[+] WeChatProcessPID: " + str(wechat_process.info['pid']))
            wechat_win_base_address = 0
            for module in wechat_process.memory_maps(grouped=False):
                if module.path and 'WeChatWin.dll' in module.path:
                    wechat_win_base_address = module.addr
                    wechat_win_base_address = wechat_win_base_address.split("-")[0]
                    wechat_win_base_address = int(wechat_win_base_address, 16)

                    file_version = get_file_version(module.path)
                    file_version_str = str(file_version)

                    tmp_rd['version'] = file_version_str

                    if file_version_str not in version_list:
                        return "[-] WeChat Current Version Is: " + file_version_str + " Not Supported"
                    else:
                        support_list = version_list[file_version_str]
                        support_list = list(support_list)
                    break
            if support_list is None:
                return "[-] WeChat Base Address Get Failed"
            else:
                wechat_key = wechat_win_base_address + support_list[4]
                hex_key = get_hex(wechat_process.pid, wechat_key)
                tmp_rd['key'] = hex_key.strip()
                if hex_key.strip() == "":
                    return "[-] WeChat Is Running, But Maybe Not Logged In"
                else:
                    wechat_name = wechat_win_base_address + support_list[0]
                    tmp_rd['name'] = get_name(wechat_process.pid, wechat_name, 100).strip()

                    wechat_account = wechat_win_base_address + support_list[1]
                    account = get_account(wechat_process.pid, wechat_account, 100).strip()
                    if account.strip() == "":
                        tmp_rd['account'] = "None"
                    else:
                        tmp_rd['account'] = account

                    wechat_mobile = wechat_win_base_address + support_list[2]
                    mobile = get_mobile(wechat_process.pid, wechat_mobile, 100).strip()
                    if mobile.strip() == "":
                        tmp_rd['mobile'] = "None"
                    else:
                        tmp_rd['mobile'] = mobile

                    wechat_mail = wechat_win_base_address + support_list[3]
                    mail = get_mail(wechat_process.pid, wechat_mail, 100).strip()
                    if mail.strip() != "":
                        tmp_rd['mail'] = mail
                    else:
                        tmp_rd['mail'] = "None"

            rd.append(tmp_rd)

    if wechat_process is None:
        return "[-] WeChat No Run"
    return rd


if __name__ == "__main__":
    version_list = json.load(open("version_list.json", "r"))
    rd = read_info(version_list)
    keys = []
    for i in rd:
        for k, v in i.items():
            if k == 'key':
                keys.append(v)
            if k == 'account':
                wechatUserAccount = v
            print("[+] {0}: {1}".format(k, v))
        print("=====================================")
    # 解密
    startDecrypted(keys, wechatUserAccount)
