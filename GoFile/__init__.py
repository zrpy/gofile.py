import httpx
import re
import urllib
import os
from tqdm import tqdm


class GofileSyncClient:
    def __init__(self, token=None, proxy=None):
        self.token = token
        self.root_id = None
        self.account_id = None
        self.wt = None
        self.session = httpx.Client(timeout=60, proxy=proxy)

    def _make_headers(self, token,download=False):
        if download:
            headers = {
                "cookie": "accountToken={}".format(self.token)
            }
            return headers
        headers = {}
        if token:
            headers["authorization"] = f"Bearer {token}"
        return headers

    def register(self):
        self.wt = self.session.get("https://gofile.io/dist/js/global.js").text.split("appdata.wt")[1].split('"')[1]
        if self.token:
            return self.token
        elif not self.token:
            res = self.session.post("https://api.gofile.io/accounts",headers=self._make_headers(None)).json()
            if res["status"] == "ok":
                self.token = res["data"]["token"]
                self.root_id = res["data"]["rootFolder"]
                self.account_id = res["data"]["id"]
                return self.token
            else:
                return ""

    def login(self,token):
        self.wt = self.session.get("https://gofile.io/dist/js/global.js").text.split("appdata.wt")[1].split('"')[1]
        res=self.session.get("https://api.gofile.io/accounts/website",headers=self._make_headers(self.token)).json()
        if res["status"]=="ok":
            self.token = res["data"]["token"]
            self.root_id = res["data"]["rootFolder"]
            self.account_id = res["data"]["id"]
            return True
        else:
            return False

    def get_info(self, code, password=None):
        if not self.token:
            raise Exception("Token isn't set.")
        if password:
            res = self.session.get("https://api.gofile.io/contents/{}?wt={}&password={}&contentFilter=&page=1&pageSize=1000&sortField=name&sortDirection=1".format(code,self.wt,password),headers=self._make_headers(self.token)).json()
        else:
            res = self.session.get("https://api.gofile.io/contents/{}?wt={}&contentFilter=&page=1&pageSize=1000&sortField=name&sortDirection=1".format(code,self.wt),headers=self._make_headers(self.token)).json()
        if res["status"] == "ok":
            return res["data"]
        return res

    def download(self,link,folder=os.getcwd()):
        if not self.token:
            raise Exception("Token isn't set.")
        with self.session.stream("GET", link,headers=self._make_headers(self.token,True)) as res:
            total = int(res.headers.get("Content-Length", 0))
            chunk_size = 1024
            expected = -(-total // chunk_size)
            file_name = urllib.parse.unquote(re.search(r'filename\*?=(?:UTF-8\'\'|")(.*?)(?:"|$)', res.headers.get("content-disposition")).group(1))
            f=open(os.path.join(folder,file_name),"wb")
            chunks = res.iter_bytes(chunk_size=chunk_size)
            bar = tqdm(
                desc="Downloading {}".format(file_name),
                total=expected,
                unit='B',
                unit_scale=True,
                unit_divisor=2048,
                leave=True,
                position=0
            )
            for chunk in chunks:
                f.write(chunk)
                bar.update(1)
            bar.close()

    def create_folder(self,folder_id=None):
        if not self.token:
            raise Exception("Token isn't set.")
        if not folder_id:
            folder_id=self.root_id
        res=self.session.post("https://api.gofile.io/contents/createfolder",headers=self._make_headers(self.token),json={"parentFolderId":folder_id,"public":True}).json()
        if res["status"] == "ok":
            return res["data"]
        return res

    def upload(self,file:os.path.join,folder_id=None):
        if not self.token:
            raise Exception("Token isn't set.")
        res=self.session.post("https://upload.gofile.io/uploadfile",data={"folderId":folder_id},headers=self._make_headers(self.token),files={"file":open(file, "rb")}).json()
        if res["status"] == "ok":
            return res["data"]
        return res

    def update(self,content_id,attribute,attribute_value):
        if not self.token:
            raise Exception("Token isn't set.")
        types={"name":str,"description":str,"tags":list,"public":bool,"expiry":int,"password":str}
        if attribute in types:
            raise Exception("The attribute is different.")
        if not types.get(attribute)==type(attribute_value):
            raise Exception("The type is different.")
        res=self.session.post("https://api.gofile.io/contents/{}/update".format(content_id),json={"attribute":attribute,"attributeValue":attribute_value},headers=self._make_headers(self.token)).json()
        if res["status"] == "ok":
            return True
        return False

    def delete_content(self, content_id):
        if not self.token:
            raise Exception("Token isn't set.")
        res=self.session.delete("https://api.gofile.io/contents",data={"contentsId":content_id},headers=self._make_headers(self.token),files={"file":open(file, "rb")}).json()
        if res["status"] == "ok":
            return True
        return False


class GofileAsyncClient:
    def __init__(self, token=None, proxy=None):
        self.token = token
        self.root_id = None
        self.account_id = None
        self.wt = None
        self.session = httpx.AsyncClient(timeout=60, proxy=proxy)

    def _make_headers(self, token,download=False):
        if download:
            headers = {
                "cookie": "accountToken={}".format(self.token)
            }
            return headers
        headers = {}
        if token:
            headers["authorization"] = f"Bearer {token}"
        return headers

    async def register(self):
        self.wt = self.session.get("https://gofile.io/dist/js/global.js").text.split("appdata.wt")[1].split('"')[1]
        if self.token:
            return self.token
        if not self.token:
            res = (await self.session.post("https://api.gofile.io/accounts",headers=self._make_headers(None))).json()
            if res["status"] == "ok":
                self.token = res["data"]["token"]
            return self.token

    async def login(self,token):
        self.wt = (await self.session.get("https://gofile.io/dist/js/global.js")).text.split("appdata.wt")[1].split('"')[1]
        res=(await self.session.get("https://api.gofile.io/accounts/website",headers=self._make_headers(self.token))).json()
        if res["status"]=="ok":
            self.token = res["data"]["token"]
            self.root_id = res["data"]["rootFolder"]
            self.account_id = res["data"]["id"]
            return True
        else:
            return False

    async def get_info(self, code, password=None):
        if not self.token:
            raise Exception("Token isn't set.")
        if password:
            res = (await self.session.get("https://api.gofile.io/contents/{}?wt={}&password={}&contentFilter=&page=1&pageSize=1000&sortField=name&sortDirection=1".format(code,self.wt,password),headers=self._make_headers(self.token))).json()
        else:
            res = (await self.session.get("https://api.gofile.io/contents/{}?wt={}&contentFilter=&page=1&pageSize=1000&sortField=name&sortDirection=1".format(code,self.wt),headers=self._make_headers(self.token))).json()
        if res["status"] == "ok":
            return res["data"]
        return res

    async def download(self,link,folder=os.getcwd()):
        if not self.token:
            raise Exception("Token isn't set.")
        async with self.session.stream("GET", link,headers=self._make_headers(self.token,True)) as res:
            total = int(res.headers.get("Content-Length", 0))
            chunk_size = 1024
            expected = -(-total // chunk_size)
            file_name = urllib.parse.unquote(re.search(r'filename\*?=(?:UTF-8\'\'|")(.*?)(?:"|$)', res.headers.get("content-disposition")).group(1))
            f=open(os.path.join(folder,file_name),"wb")
            chunks = res.aiter_bytes(chunk_size=chunk_size)
            bar = tqdm(
                desc="Downloading {}".format(file_name),
                total=expected,
                unit='B',
                unit_scale=True,
                unit_divisor=2048,
                leave=True,
                position=0
            )
            async for chunk in chunks:
                f.write(chunk)
                bar.update(1)
            bar.close()

    async def create_folder(self,folder_id=None):
        if not self.token:
            raise Exception("Token isn't set.")
        if not folder_id:
            folder_id=self.root_id
        res=(await self.session.post("https://api.gofile.io/contents/createfolder",headers=self._make_headers(self.token),json={"parentFolderId":folder_id,"public":True})).json()
        return res

    async def upload(self,file:os.path.join,folder_id=None):
        if not self.token:
            raise Exception("Token isn't set.")
        res=(await self.session.post("https://upload.gofile.io/uploadfile",data={"folderId":folder_id},headers=self._make_headers(self.token),files={"file":open(file, "rb")})).json()
        if res["status"] == "ok":
            return res["data"]
        return res

    async def update(self,content_id,attribute,attribute_value):
        if not self.token:
            raise Exception("Token isn't set.")
        types={"name":str,"description":str,"tags":list,"public":bool,"expiry":int,"password":str}
        if attribute in types:
            raise Exception("The attribute is different.")
        if not types.get(attribute)==type(attribute_value):
            raise Exception("The type is different.")
        res=(await self.session.post("https://api.gofile.io/contents/{}/update".format(content_id),json={"attribute":attribute,"attributeValue":attribute_value},headers=self._make_headers(self.token))).json()
        if res["status"] == "ok":
            return True
        return False

    async def delete_content(self, content_id):
        if not self.token:
            raise Exception("Token isn't set.")
        res=(await self.session.delete("https://api.gofile.io/contents",data={"contentsId":content_id},headers=self._make_headers(self.token),files={"file":open(file, "rb")})).json()
        if res["status"] == "ok":
            return True
        return False
