# -*- coding: utf-8 -*-
from Chaopan import Chaopan

filepath = input("请输入文件路径(不大于200MB):")

print("请耐心等待文件上传")

try:
    with open(filepath, 'rb') as f:
        ret = Chaopan.upload_file(f)
except Exception as e: 
    print(f'出现错误，原因为:{str(e)}')
else:
    if ret["status"]:
        print(f'下载直链为(http替换为https仍然可用)： {ret["att_file"]["att_clouddisk"]["downPath"]}')
        print(f'分享链接为： {ret["att_file"]["att_clouddisk"]["shareUrl"]}')
    else:
        print(f'转直链失败，原因为{ret["msg"]}')

