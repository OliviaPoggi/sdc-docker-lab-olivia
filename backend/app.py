"""FastAPI backend.

Receives an uploaded image, applies the requested filter with Pillow and
returns the processed image. It has no user interface: the Streamlit
frontend is the one that talks to it, over the Docker Compose network.
"""
import io

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from PIL import Image, ImageFilter, ImageOps, UnidentifiedImageError

app = FastAPI(title="Image Processing API")

FILTERS = ["grayscale", "blur", "rotate", "invert", "edges"]


@app.get("/health")
def health():
    """Used by the frontend to show whether the backend is reachable."""
    return {"status": "ok"}


@app.get("/filters")
def list_filters():
    """The frontend asks for this to build its dropdown."""
    return {"filters": FILTERS}


@app.post("/process")
async def process_image(
    file: UploadFile = File(...),
    filter_name: str = Form("grayscale"),
    amount: int = Form(5),
):
    """Apply one filter to the uploaded image and return the result as PNG.

    `amount` means different things per filter: blur radius for "blur",
    degrees for "rotate", and it is ignored by the others.
    """
    if filter_name not in FILTERS:
        raise HTTPException(status_code=422, detail=f"Unknown filter: {filter_name}")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=422, detail="The uploaded file is empty")

    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=422, detail="That file is not a readable image")

    image = image.convert("RGB")

    if filter_name == "grayscale":
        image = ImageOps.grayscale(image)
    elif filter_name == "blur":
        image = image.filter(ImageFilter.GaussianBlur(radius=amount))
    elif filter_name == "rotate":
        image = image.rotate(amount, expand=True)
    elif filter_name == "invert":
        image = ImageOps.invert(image)
    elif filter_name == "edges":
        image = image.filter(ImageFilter.FIND_EDGES)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    return Response(content=buffer.getvalue(), media_type="image/png")
