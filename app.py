from fastapi import FastAPI, Query
from fastapi.responses import Response
import requests

app = FastAPI()

@app.get("/image_proxy")
def image_proxy(
    pixiv_url: str = Query(..., description="Pixiv 圖片 URL")
):
    headers = {
        "Referer": "https://www.pixiv.net/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
    }

    try:
        res = requests.get(pixiv_url, headers=headers, timeout=15)

        if res.status_code == 200:
            # 自動判斷格式，避免 media_type 固定寫死 image/jpeg
            content_type = res.headers.get("Content-Type", "image/jpeg")
            return Response(content=res.content, media_type=content_type)

        elif res.status_code == 403:
            return Response(content=b"403 Forbidden (可能 Pixiv 擋 IP 或需 cookie)", status_code=403)

        elif res.status_code == 404:
            return Response(content=b"Image not found", status_code=404)

        else:
            return Response(
                content=f"Unexpected error. Status: {res.status_code}".encode(),
                status_code=res.status_code
            )

    except requests.exceptions.RequestException as e:
        return Response(
            content=f"Request exception: {str(e)}".encode(),
            status_code=500
        )

