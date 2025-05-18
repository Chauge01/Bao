from fastapi import FastAPI
from pixivpy3 import AppPixivAPI
import requests
import base64
import os
from dotenv import load_dotenv

# 讀取 .env 的 refresh_token
load_dotenv()
REFRESH_TOKEN = os.getenv("PIXIV_REFRESH_TOKEN")

app = FastAPI()
api = AppPixivAPI()
api.auth(refresh_token=REFRESH_TOKEN)

@app.get("/")
def root():
    return {"message": "PixivPy API is working!"}

@app.get("/illust/{illust_id}")
def get_illust_info(illust_id: int):
    try:
        result = api.illust_detail(illust_id)
        illust = result.illust

        # 圖片網址
        image_url = illust.image_urls.large

        # 抓圖並轉成 base64
        headers = {"Referer": "https://www.pixiv.net/"}
        image_response = requests.get(image_url, headers=headers)
        image_base64 = base64.b64encode(image_response.content).decode("utf-8")

        return {
            "illust_id": illust_id,
            "title": illust.title,
            "tags": [tag.name for tag in illust.tags],
            "image_url": image_url,
            "image_base64": f"data:image/jpeg;base64,{image_base64}"
        }
    except Exception as e:
        return {"error": str(e)}

#250512 更
#250518 更

