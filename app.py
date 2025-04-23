from fastapi import FastAPI
from pydantic import BaseModel
from gradio_client import Client
import base64
from io import BytesIO
from PIL import Image

app = FastAPI()
client = Client("danny35913/CLIP-Interrogator-2")  # 換成你的 Hugging Face Space ID

# ─── API: 用 URL 推論 ─────────────────────────────
class InferenceRequest(BaseModel):
    image_url: str
    mode: str = "best"
    best_max_flavors: int = 4

@app.post("/clipi2")
def run_clip(req: InferenceRequest):
    result = client.predict(
        image_url=req.image_url,
        mode=req.mode,
        best_max_flavors=req.best_max_flavors,
        api_name="/clipi2"
    )
    return {"result": result}

# ─── API: 用 Base64 圖片推論 ────────────────────────
class InferenceBase64Request(BaseModel):
    image_base64: str
    mode: str = "best"
    best_max_flavors: int = 4

@app.post("/clipi2_from_base64")
def run_clip_base64(req: InferenceBase64Request):
    try:
        header, encoded = req.image_base64.split(",", 1)
        image_data = base64.b64decode(encoded)
        image = Image.open(BytesIO(image_data)).convert("RGB")

        buf = BytesIO()
        image.save(buf, format="JPEG")
        buf.seek(0)

        result = client.predict(
            image=buf,
            mode=req.mode,
            best_max_flavors=req.best_max_flavors,
            api_name="/clipi2"
        )
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}




