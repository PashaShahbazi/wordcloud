from io import BytesIO
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

from create_wordcloud import create_cloud, create_cloud_mask


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


@app.post("/api/wordcloud")
async def wordcloud_api(
    text: str = Form(min_length=1),
    background_color: str = Form(default="black"),
    width: int = Form(default=800, ge=100, le=3000),
    height: int = Form(default=600, ge=100, le=3000),
    mask: UploadFile | None = File(default=None),
):
    output_path = GENERATED_DIR / "wordcloud.png"

    if mask is None:
        cloud = create_cloud(
            text,
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
        cloud = create_cloud_mask(text, background_color, mask_array)

    cloud.to_file(str(output_path))

    return {
        "success": True,
        "image_url": "/generated/wordcloud.png",
        "width": width,
        "height": height,
    }
