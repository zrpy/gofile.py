import httpx
import re
import urllib
import os
from tqdm import tqdm


class GofileSyncClient:
    def __init__(self, token=None, proxy=None):
        self.token = token
        self.session = httpx.Client(timeout=60)

    def _make_headers(self, token,download=False):
        if download:
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "sec-ch-ua": "\"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": "\"Android\"",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-site",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "cookie": "accountToken={}".format(self.token),
                "Referer": "https://gofile.io/",
                "Referrer-Policy": "origin"
            }
            return headers
        headers = {
            "accept": "*/*",
            "accept-language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": '"Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "Referer": "https://gofile.io/",
            "Referrer-Policy": "origin",
        }
        if token:
            headers["authorization"] = f"Bearer {token}"
        return headers

    def register(self):
        if self.token:
            return self.token
        if not self.token:
            res = self.session.post("https://api.gofile.io/accounts",headers=self._make_headers(None)).json()
            if res["status"] == "ok":
                self.token = res["data"]["token"]
            return self.token

    def login(self,token):
        self.token=token

    def get_links(self, code):
        if not self.token:
            raise Exception("Token isn't set.")
        wt = self.session.get("https://gofile.io/dist/js/global.js").text.split("appdata.wt")[1].split('"')[1]
        res = self.session.get(f"https://api.gofile.io/contents/{code}?wt={wt}&contentFilter=&page=1&pageSize=1000&sortField=name&sortDirection=1",headers=self._make_headers(self.token))
        data = res.json()
        if data["status"] == "ok":
            return data["data"]
        return data

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


class GofileAsyncClient:
    def __init__(self, token=None, proxy=None):
        self.token = token
        self.session = httpx.AsyncClient(proxy=proxy,timeout=60)

    def _make_headers(self, token,download=False):
        if download:
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "sec-ch-ua": "\"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": "\"Android\"",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-site",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "cookie": "accountToken={}".format(self.token),
                "Referer": "https://gofile.io/",
                "Referrer-Policy": "origin"
            }
            return headers
        headers = {
            "accept": "*/*",
            "accept-language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": '"Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "Referer": "https://gofile.io/",
            "Referrer-Policy": "origin",
        }
        if token:
            headers["authorization"] = f"Bearer {token}"
        return headers

    async def register(self):
        if self.token:
            return self.token
        if not self.token:
            res = (await self.session.post("https://api.gofile.io/accounts",headers=self._make_headers(None))).json()
            if res["status"] == "ok":
                self.token = res["data"]["token"]
            return self.token

    async def login(self,token):
        self.token=token

    async def get_links(self, code):
        if not self.token:
            raise Exception("Token isn't set.")
        wt = (await self.session.get("https://gofile.io/dist/js/global.js")).text.split("appdata.wt")[1].split('"')[1]
        res = await self.session.get(f"https://api.gofile.io/contents/{code}?wt={wt}&contentFilter=&page=1&pageSize=1000&sortField=name&sortDirection=1",headers=self._make_headers(self.token))
        data = res.json()
        if data["status"] == "ok":
            return data["data"]
        return data

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
