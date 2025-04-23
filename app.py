from fastapi import FastAPI
from pydantic import BaseModel
from gradio_client import Client

app = FastAPI()
client = Client("danny35913/CLIP-Interrogator-2")  # 改成你的 Space ID

# 用 URL 做推論
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

# 用 Base64 字串做推論
class InferenceBase64Request(BaseModel):
    image_base64: str
    mode: str = "best"
    best_max_flavors: int = 4

@app.post("/clipi2_from_base64")
def run_clip_base64(req: InferenceBase64Request):
    try:
        result = client.predict(
    req.image_base64,     # ✅ 第一個 input：image base64 string
    req.mode,             # ✅ 第二個 input
    req.best_max_flavors, # ✅ 第三個 input
    api_name="/clipi2_from_base64"
)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
