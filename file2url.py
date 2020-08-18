# -*- coding: utf-8 -*-
from Chaopan import Chaopan
import json
import sys

def getsize(file):
    rr = file.tell()
    size = file.seek(0, 2)
    file.seek(0, rr)
    return size

def callback(per):
    hashes = '#' * int(per * 30)
    spaces = ' ' * (30 - len(hashes))
    sys.stdout.write("\rPercent: [%s] %d%%"%(hashes + spaces, per*100))
    sys.stdout.flush()

filepath = input("请输入文件路径： ")

try:
    with open(filepath, 'rb') as f:
        size = getsize(f)
        if size <= 200000000:
            print("正在上传中，请等待...")
            ret = Chaopan.upload_share_file(f)
            if ret["status"]:
                print(f'下载直链为(http替换为https仍然可用)： {ret["att_file"]["att_clouddisk"]["downPath"]}')
                print(f'分享链接为： {ret["att_file"]["att_clouddisk"]["shareUrl"]}')
            else:
                print(f'转直链失败，原因为{ret["msg"]}')
        else:
            print("您的文件大于200M, 正在以登录状态上传，请等待...")
            with open('config.json', 'rb') as cf:
                dataobj = json.load(cf)
            cp = Chaopan(dataobj)
            retobj = cp.upload_file(f, callback=callback)
            print("")
            print(f'下载直链为(http替换为https仍然可用)： http://d0.ananas.chaoxing.com/download/{retobj["objectId"]}')
            print(f'分享链接为： http://cloud.ananas.chaoxing.com/view/fileview?objectid={retobj["objectId"]}')
            print('正在清理网盘空间(清理后上传的文件不会占用您的网盘空间)')
            if "id" in retobj:
                cp.del_file(retobj["id"])
            elif "resid" in retobj:
                cp.del_file(retobj["resid"])
            print('清理完成')

except Exception as e: 
    print(f'出现错误，原因为:{str(e)}')
