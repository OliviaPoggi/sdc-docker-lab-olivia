# Docker Compose Lab - Image Processing

Module 4 assignment for Solution Deployment & Communication.

Two containers started together with Docker Compose: a Streamlit frontend
where you upload an image and choose a filter, and a FastAPI backend that
applies the filter and sends the image back.

## How to run

    docker compose up --build

Then open http://localhost:8501, upload an image, pick a filter and click
"Apply filter". To stop it, `docker compose down`.

The backend docs are at http://localhost:8000/docs.

## How the two containers talk to each other

Compose puts both containers on the same network, `app-network`. The frontend
finds the backend by its service name, `backend`, which Docker resolves to
the right container, so there is no IP address written anywhere.

The address arrives through the `APP_BACKEND_URL` environment variable, set
in docker-compose.yml. Without the shared network the two containers would be
isolated and the frontend could not reach the backend at all.

## Filters

grayscale, blur, rotate, invert, edges.

Blur and rotate use the slider (blur radius and degrees). The other three
ignore it.

## Backend endpoints

- `POST /process` takes the image, the filter name and the amount, and
  returns the processed image as PNG
- `GET /filters` returns the list of filters, used to fill the dropdown
- `GET /health` is what the frontend calls to show if the backend is up

## Files

    backend/    FastAPI app, Dockerfile, requirements.txt
    frontend/   Streamlit app, Dockerfile, requirements.txt
    docker-compose.yml

## Testing

I tested all five filters in the browser. Grayscale, invert and edges keep
the original size. Blur gets stronger as the radius goes up. Rotating 90
degrees swaps the width and the height, because the canvas grows to fit the
rotated image instead of cropping it.

Uploading a file that is not an image returns a 422 error instead of
crashing, and so does asking for a filter that does not exist.