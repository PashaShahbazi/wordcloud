from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from create_wordcloud import create_cloud


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
async def wordcloud_api(
    text: str = Form(min_length=1),
    background_color: str = Form(default="black"),
    width: int = Form(default=800, ge=100, le=3000),
    height: int = Form(default=600, ge=100, le=3000),
):
    output_path = GENERATED_DIR / "wordcloud.png"

    cloud = create_cloud(
        text,
        background_color,
        width=width,
        height=height,
    )

    cloud.to_file(str(output_path))

    return {
        "success": True,
        "image_url": "/generated/wordcloud.png",
        "width": width,
        "height": height,
    }
