from io import BytesIO
from pathlib import Path
from typing import Literal

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

from create_wordcloud import create_cloud, create_cloud_mask
from get_wiki import WikipediaLookupError, wiki_get
from text_processing import normalize_text


app = FastAPI(title="WordCloud API")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
GENERATED_DIR = BASE_DIR / "generated"
MAX_MASK_BYTES = 5 * 1024 * 1024
MAX_MASK_DIMENSION = 3000

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


def prepare_mask(mask_bytes, width, height):
    if len(mask_bytes) > MAX_MASK_BYTES:
        raise HTTPException(status_code=413, detail="Mask image must be 5 MB or smaller.")

    try:
        with Image.open(BytesIO(mask_bytes)) as image:
            if image.format != "PNG":
                raise HTTPException(
                    status_code=400,
                    detail="Mask image must be a PNG file.",
                )

            if (
                image.width > MAX_MASK_DIMENSION
                or image.height > MAX_MASK_DIMENSION
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Mask dimensions must not exceed 3000x3000 pixels.",
                )

            resized_mask = image.convert("L").resize(
                (width, height),
                Image.Resampling.NEAREST,
            )
            return np.array(resized_mask)
    except HTTPException:
        raise
    except (Image.DecompressionBombError, UnidentifiedImageError, OSError) as error:
        raise HTTPException(
            status_code=400,
            detail="Mask image is not a valid PNG file.",
        ) from error


async def resolve_source_text(source_mode, text, wikipedia_subject):
    if source_mode == "text":
        if not text or not text.strip():
            raise HTTPException(status_code=422, detail="Text cannot be empty.")
        return text

    if not wikipedia_subject or not wikipedia_subject.strip():
        raise HTTPException(
            status_code=422,
            detail="Wikipedia subject cannot be empty.",
        )

    subject = wikipedia_subject.strip()

    try:
        article_text = await run_in_threadpool(wiki_get, subject)
    except WikipediaLookupError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    normalized_text = normalize_text(article_text)
    if not normalized_text:
        raise HTTPException(
            status_code=400,
            detail="The Wikipedia article did not contain any usable text.",
        )

    return normalized_text


@app.post("/api/wordcloud")
async def wordcloud_api(
    source_mode: Literal["text", "wikipedia"] = Form(default="text"),
    text: str | None = Form(default=None),
    wikipedia_subject: str | None = Form(default=None, max_length=200),
    background_color: str = Form(default="black"),
    width: int = Form(default=800, ge=100, le=3000),
    height: int = Form(default=600, ge=100, le=3000),
    mask: UploadFile | None = File(default=None),
):
    output_path = GENERATED_DIR / "wordcloud.png"
    source_text = await resolve_source_text(source_mode, text, wikipedia_subject)

    if mask is None:
        cloud = create_cloud(
            source_text,
            background_color,
            width=width,
            height=height,
        )
    else:
        try:
            mask_bytes = await mask.read(MAX_MASK_BYTES + 1)
        finally:
            await mask.close()

        mask_array = prepare_mask(mask_bytes, width, height)
        cloud = create_cloud_mask(source_text, background_color, mask_array)

    cloud.to_file(str(output_path))

    return {
        "success": True,
        "image_url": "/generated/wordcloud.png",
        "width": width,
        "height": height,
    }
