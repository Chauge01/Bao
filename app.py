from fastapi import FastAPI, Query
from pixivpy3 import AppPixivAPI
from dotenv import load_dotenv
import os
import time
import requests
import base64

load_dotenv()
REFRESH_TOKEN = os.getenv("PIXIV_REFRESH_TOKEN")

app = FastAPI()
api = AppPixivAPI()
api.auth(refresh_token=REFRESH_TOKEN)

headers = {
    "Referer": "https://www.pixiv.net/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
}


@app.get("/search_illust")
def search_illust(
    word: str = Query(..., description="搜尋關鍵字"),
    max_pages: int = Query(50, description="最多翻頁數，預設 50 頁")
):
    all_results = []

    result = api.search_illust(
        word,
        search_target="partial_match_for_tags",
        sort="popular_desc"
    )

    current_page = 1
    while current_page <= max_pages and result.illusts:
        print(f"📄 抓取第 {current_page} 頁，共 {len(result.illusts)} 張")

        for i in result.illusts:
            # 確保有 medium 圖片
            if not hasattr(i, "image_urls") or not hasattr(i.image_urls, "medium"):
                print(f"⚠️ 跳過一張缺圖的作品：{i.id}")
                continue

            # 優先使用 medium 版本（穩定格式），避免 WebP / forbidden
            image_url = i.image_urls.medium

            try:
                image_response = requests.get(image_url, headers=headers, timeout=15)
                if image_response.status_code == 200:
                    image_base64 = base64.b64encode(image_response.content).decode("utf-8")
                    image_base64_data = f"data:image/jpeg;base64,{image_base64}"
                else:
                    print(f"❌ HTTP 狀態碼 {image_response.status_code}，圖片 ID：{i.id}")
                    image_base64_data = None
            except Exception as e:
                print(f"❗ 圖片抓取錯誤：{e}")
                image_base64_data = None

            # 原圖網址（非必要）
            original_url = None
            if hasattr(i, "meta_single_page") and i.meta_single_page:
                original_url = i.meta_single_page.get("original_image_url")

            all_results.append({
                "illust_id": i.id,
                "title": i.title,
                "tags": [t.name for t in i.tags],
                "image_url_medium": i.image_urls.medium,
                "image_url_large": i.image_urls.large,
                "image_url_square": i.image_urls.square_medium,
                "original_url": original_url,
                "user_name": i.user.name,
                "page_url": f"https://www.pixiv.net/en/artworks/{i.id}" 
            })

        next_qs = api.parse_qs(result.next_url)
        if not next_qs:
            break

        #     "image_base64": image_base64_data, 先拿掉 檔案太大，但之後可以放回來～

        time.sleep(4)
        result = api.search_illust(**next_qs)
        current_page += 1

    return {
        "keyword": word,
        "total_images": len(all_results),
        "images": all_results
    }

