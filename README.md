# GoFile.py
gofile.io wrapper in python
```py
# 同期
client = GofileSyncClient()
print(client.register())# show the token and register the account
# client.login("token") Log in to the account
link=client.get_links("code")
for i in link["children"]:
    client.download(link["children"][i]["link"],os.getcwd())
# 非同期
async def main():
    client = GofileAsyncClient()
    print(await client.register())# show the token
    # login await client.login("token")
    link=await client.get_links("code")
    for i in link["children"]:
        await client.download(link["children"][i]["link"],os.getcwd())
asyncio.run(main())
```
## What to update.
1. Upload files
2. Show the folder info
