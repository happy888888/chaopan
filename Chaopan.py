# -*- coding: utf-8 -*-
import requests,json
from ftplib import FTP
import os,time

class Chaopan(object):
    def __init__(self, cookies):
        """登录超盘"""
        session = requests.session()
        requests.utils.add_dict_to_cookiejar(session.cookies, cookies)
        response = session.get('https://pan-yz.chaoxing.com/api/token/uservalid')
        retobj = json.loads(response.text)
        if not retobj["result"]:
            raise Exception("参数验证失败，登录状态失效")
        self.__token = retobj["_token"]
        self.__id = cookies["UID"]
        self.__session = session

    def get_disk_capacity(self):
        """获取总空间和已用空间大小"""
        url = f'https://pan-yz.chaoxing.com/api/getUserDiskCapacity?puid={self.__id}&_token={self.__token}'
        response = self.__session.get(url)
        retobj = json.loads(response.text)
        '''
        {"code":2,"data":{"diskTotalCapacity":107374182400,"diskUsedCapacity":4762292405},"newCode":200001,"result":true}
        '''
        return retobj

    def list_dir(self, fldid='', orderby='d', order='desc', page=1, size=100, addrec=False, showCollect=1):
        """列举目录文件"""
        url = f'https://pan-yz.chaoxing.com/api/getMyDirAndFiles?puid={self.__id}&fldid={fldid}&orderby={orderby}&order={order}&page={page}&size={size}&_token={self.__token}&addrec={addrec}&showCollect={showCollect}'
        response = self.__session.get(url)
        retobj = json.loads(response.text)
        '''
        {"result":true,"shareCount":0,"data":[{"preview":"http://pan-yz.chaoxing.com/preview/showpreview_502434490360643584.html","filetype":"","extinfo":"","thumbnail":"http://pan-yz.chaoxing.com/thumbnail/origin/d9306333d36579b7ba8047234a4ad7b9?type=video","creator":137386368,"modifyDate":1597719316000,"resTypeValue":1,"sort":20,"suffix":"mp4","resid":502434490360643584,"topsort":0,"restype":"RES_TYPE_YUNPAN_FILE","duration":2546,"pantype":"USER_PAN","puid":137386368,"size":128644721,"uploadDate":1597719316000,"filepath":"","crc":"a3903ee56a4f131c7d23ce796f92ea4d","isfile":true,"name":"【 同人音声 】想用治愈的震动声让他入睡.mp4","residstr":"502434490360643584","objectId":"d9306333d36579b7ba8047234a4ad7b9"},{"preview":"","filetype":"","extinfo":"","thumbnail":"","creator":137386368,"modifyDate":1597647440000,"resTypeValue":2,"sort":9,"suffix":"","resid":502133017096220672,"topsort":0,"restype":"RES_TYPE_YUNPAN_FOLDER","duration":0,"pantype":"USER_PAN","puid":137386368,"size":0,"uploadDate":1597647440000,"filepath":"","isfile":false,"name":"电影","residstr":"502133017096220672"}],"curDir":451731192771985408}
        '''
        return retobj

    def __create_file_new(self, file: "本地文件", fldid=""):
        url = 'https://pan-yz.chaoxing.com/opt/createfilenew'
        BYTES_PER_CHUNK = 512 * 1024
        LIMIT = 1024 * 1024
        ffile = []
        rr = file.tell()
        size = file.seek(0, 2)
        file.seek(0, 0)
        ffile.append(file.read(BYTES_PER_CHUNK))
        file.seek(BYTES_PER_CHUNK + size - LIMIT, 0)
        ffile.append(file.read(BYTES_PER_CHUNK))
        file.seek(0, rr)

        path,name = os.path.split(file.name)

        files = {
            "file0":(ffile[0]),
            "file1":(ffile[1])
            }
        post_data = {
            "size": size,
            "fn": name,
            "puid":0,
            }
        if fldid:
            post_data["fldid"] = fldid

        response = self.__session.post(url, data=post_data, files=files)
        return json.loads(response.text)

    def __ftp_upload_file(self, file: "本地文件", timemil, callback=None):
        jindu = [file.seek(0, 2),0]
        def __callback(block):
            jindu[1] += 8192
            if jindu[1] < jindu[0]:
                callback(jindu[1] / jindu[0])
            else:
                callback(1)

        ip = '140.210.72.122'
        ftp = FTP()
        ftp.connect(ip, 21)
        ftp.login("usertemp", "0GYF0hBAbsXVBZCUPaSOVS")
        ftp.set_pasv(True)
        ftp.mkd(f'/384/2432/{self.__id}/{timemil}')
        path,name = os.path.split(file.name)
        file.seek(0, 0)
        if callback:
            res = ftp.storbinary(f'STOR /384/2432/{self.__id}/{timemil}/{name}', file, blocksize=8192, callback=__callback)
        else:
            res = ftp.storbinary(f'STOR /384/2432/{self.__id}/{timemil}/{name}', file)
        ret =  res.find('226') != -1
        ftp.quit()
        return ret

    def __sync_upload(self, timemil, pntid=""):
        url = 'https://pan-yz.chaoxing.com/api/notification/rsyncsucss'
        post_data = {
            "puid": self.__id,
            "rf": timemil,
            "_token": self.__token
            }
        if pntid:
            post_data["pntid"] = pntid

        response = self.__session.post(url, data=post_data)
        return json.loads(response.text)

    def __crcstatus(self, crc):
        url = f'https://pan-yz.chaoxing.com/api/crcstatus?puid={self.__id}&crc={crc}&_token={self.__token}'
        response = requests.get(url)
        return json.loads(response.text)

    def upload_file(self, file: "本地文件", fldid="", callback=None):
        """上传文件"""
        size = Chaopan.__getsize(file)
        if size > 1024 * 1024 + 1024 * 1024:
            retobj = self.__create_file_new(file, fldid)
            if retobj["result"]:
                return retobj["data"]

            crc = retobj["crc"]
            timemil = retobj["timemil"]

            if self.__ftp_upload_file(file, timemil, callback):
                self.__sync_upload(timemil, fldid)

            return self.__crcstatus(crc)

        else:
            timemil = int(time.time() * 1000)
            self.__ftp_upload_file(file, timemil, callback)
            return  self.__sync_upload(timemil, fldid)

    def del_file(self, id: '文件id，多个请用英文逗号","分隔'):
        """删除网盘上文件"""
        url = 'https://pan-yz.chaoxing.com/api/delete'
        post_data = {
            "puid": self.__id,
            "resids": id,
            "_token": self.__token
            }
        response = self.__session.post(url, data=post_data)
        return json.loads(response.text)

    @staticmethod
    def upload_share_file(file: "本地文件或Bytes"):
        """上传本地文件转链接,不得大于200M"""
        size = Chaopan.__getsize(file)
        if size == 0 or size > 200000000:
            return {"status":False,"msg":"文件大小必须在0-200MB之间"}
        url = 'http://notice.chaoxing.com/pc/files/uploadNoticeFile'
        file_data = {
            'attrFile': file
            }
        response = requests.post(url, files=file_data)
        return json.loads(response.text)

    @staticmethod
    def __getsize(file):
        """获取文件大小"""
        import _io
        if isinstance(file, _io.BufferedReader):
            rr = file.tell()
            size = file.seek(0, 2)
            file.seek(0, rr)
            return size
        elif isinstance(file, bytes):
            return len(file)
        else:
            return 0
