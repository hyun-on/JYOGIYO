import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse, unquote
from urllib.request import urlretrieve
import os


URL = 'https://www.yupdduk.com/sub/hotmenu?mode=1'

url = urlparse(URL)

req = requests.get(URL)
html = req.text
header = req.headers
status = req.status_code
is_ok = req.ok

if status == 200:
    soup = bs(html, 'html.parser')

images = soup.select('img')

imgList = list()

for image in images:
    src = image.get('src')
    if src.startswith('/'):
        src = url.scheme + '://' + url.netloc + src
    imgList.append(src)

print(imgList)

os.makedirs('downloads', exist_ok=True)
for img in imgList:
    imgurl = img
    if img.startswith('/'):
        imgurl = url.scheme + '://' + url.netloc + img
    savepath = 'downloads/' + imgurl.split('/')[-1].replace('?', '')

    with open(savepath, "wb") as file:
        response = requests.get(imgurl)
        file.write(response.content)

print('Done!')
