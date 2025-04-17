from fastapi import FastAPI
from pydantic import BaseModel
from gradio_client import Client

app = FastAPI()
client = Client("danny35913/CLIP-Interrogator-2")  # 改成你的 Space ID

class InferenceRequest(BaseModel):
    image_url: str
    mode: str = "best"
    best_max_flavors: int = 4

@app.post("/interrogate")
def run_clip(req: InferenceRequest):
    result = client.predict(
        image_url=req.image_url,
        mode=req.mode,
        best_max_flavors=req.best_max_flavors,
        api_name="/clipi2"
    )
    return {"result": result}
