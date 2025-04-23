from fastapi import FastAPI, Query
from pixivpy3 import AppPixivAPI
from dotenv import load_dotenv
import os

load_dotenv()
REFRESH_TOKEN = os.getenv("PIXIV_REFRESH_TOKEN")

app = FastAPI()
api = AppPixivAPI()
api.auth(refresh_token=REFRESH_TOKEN)

@app.get("/search_illust")
def search_illust(
    word: str = Query(..., description="搜尋關鍵字"),
    max_pages: int = Query(30, description="最多翻頁數，預設 30 頁")
):
    all_results = []
    result = api.search_illust(
        word,
        search_target="partial_match_for_tags",
        sort="date_desc"
    )

    current_page = 1
    while current_page <= max_pages and result.illusts:
        print(f"📄 抓取第 {current_page} 頁，共 {len(result.illusts)} 張")

        for i in result.illusts:
            if not hasattr(i, "image_urls") or not hasattr(i.image_urls, "large"):
                continue

            # 嘗試取得原圖（不是每張都有）
            original_url = None
            if hasattr(i, "meta_single_page") and i.meta_single_page:
                original_url = i.meta_single_page.get("original_image_url")

            all_results.append({
                "illust_id": i.id,
                "title": i.title,
                "tags": [t.name for t in i.tags],
                "image_url_large": i.image_urls.large,  # 建議送 CLIP 用這個
                "image_url_medium": i.image_urls.medium,
                "image_url_square": i.image_urls.square_medium,
                "original_url": original_url,
                "user_name": i.user.name
            })

        next_qs = api.parse_qs(result.next_url)
        if not next_qs:
            break

        result = api.search_illust(**next_qs)
        current_page += 1

    return {
        "keyword": word,
        "total_images": len(all_results),
        "images": all_results
    }


