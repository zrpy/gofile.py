# GoFile.py
gofile.io wrapper in python
```py
import GoFile,os
# 同期
client = GoFile.GofileSyncClient()
print(client.register())# show the token and register the account
# client.login("token") Login to the account
link=client.get_links("code")
for i in link["children"]:
    client.download(link["children"][i]["link"],os.getcwd())
client.upload(os.path.join(os.getcwd(),"example.txt"),folder_id="")# Upload the file, no folder_id is required
client.update("ContentID","attribute" "value") # Could change name,description,tags,public,expiry,password
client.delete_content("ContentId")# Delete the file.
# 非同期
async def main():
    client = GoFile.GofileAsyncClient()
    print(await client.register())# show the token and register the account
    # login await client.login("token")
    link=await client.get_links("code")
    for i in link["children"]:
        await client.download(link["children"][i]["link"],os.getcwd())
    await client.upload(os.path.join(os.getcwd(),"example.txt"),folder_id="")#Upload the file, no folder_id is required
    await client.update("ContentID","attribute" "value") # Could change name,description,tags,public,expiry,password
    await client.delete_content("ContentId")# Delete the file.

asyncio.run(main())
```
## What to update.
1. Create special classes for functions for easy use 
