from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from create_wordcloud import create_cloud


class WordCloudInput(BaseModel):
    text: str = Field(min_length=1)
    background_color: str = "black"
    width: int = Field(default=800, ge=100, le=3000)
    height: int = Field(default=600, ge=100, le=3000)


app = FastAPI(title="WordCloud API")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
GENERATED_DIR = BASE_DIR / "generated"

GENERATED_DIR.mkdir(exist_ok=True)


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)

app.mount(
    "/generated",
    StaticFiles(directory=GENERATED_DIR),
    name="generated",
)


@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/wordcloud")
async def wordcloud_api(data: WordCloudInput):
    output_path = GENERATED_DIR / "wordcloud.png"

    cloud = create_cloud(
        data.text,
        data.background_color,
        width=data.width,
        height=data.height,
    )

    cloud.to_file(str(output_path))

    return {
        "success": True,
        "image_url": "/generated/wordcloud.png",
        "width": data.width,
        "height": data.height,
    }
