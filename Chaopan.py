import requests,json

class Chaopan(object):

    @staticmethod
    def upload_file(file: "本地文件或Bytes"):
        """上传本地文件转链接,不得大于200M"""
        size = Chaopan.__getsize(file)
        if size == 0 or size > 209715100:
            return {"status":False,"msg":"文件大小必须在0-200MB之间"}
        url = 'http://notice.chaoxing.com/pc/files/uploadNoticeFile'
        file_data = {
            'attrFile': file
            }
        content = requests.post(url, files=file_data)
        return json.loads(content.text)

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
