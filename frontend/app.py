"""Streamlit frontend.

Uploads an image, sends it to the FastAPI backend to be processed, and shows
the result next to the original.

The backend address comes from the APP_BACKEND_URL environment variable,
which Docker Compose sets to http://backend:8000. "backend" is the service
name in docker-compose.yml, and Compose's internal DNS resolves it, so no IP
address is hardcoded anywhere.
"""
import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("APP_BACKEND_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="Image Processing", layout="centered")
st.title("Image Processing")
st.caption("Streamlit frontend and FastAPI backend, in two containers")


def backend_is_up():
    try:
        return requests.get(f"{BACKEND_URL}/health", timeout=5).status_code == 200
    except requests.RequestException:
        return False


with st.sidebar:
    st.subheader("Backend")
    if backend_is_up():
        st.success("Reachable")
    else:
        st.error("Not reachable")
    st.caption(BACKEND_URL)
    if st.button("Check again"):
        st.rerun()


uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is None:
    st.info("Upload an image to get started.")
else:
    filter_name = st.selectbox(
        "Filter", ["grayscale", "blur", "rotate", "invert", "edges"]
    )

    # Only two of the filters take a value, so the slider is only shown then.
    if filter_name == "blur":
        amount = st.slider("Blur radius", 1, 20, 5)
    elif filter_name == "rotate":
        amount = st.slider("Degrees", 0, 360, 90)
    else:
        amount = 0

    if st.button("Apply filter", type="primary"):
        with st.spinner("Processing..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/process",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue())},
                    data={"filter_name": filter_name, "amount": amount},
                    timeout=60,
                )
            except requests.RequestException as error:
                st.error(f"Could not reach the backend: {error}")
                st.stop()

        if response.status_code != 200:
            st.error(f"Backend error {response.status_code}")
            st.caption(response.text[:300])
            st.stop()

        left, right = st.columns(2)
        with left:
            st.caption("Original")
            st.image(uploaded_file, use_column_width=True)
        with right:
            st.caption(f"After: {filter_name}")
            st.image(response.content, use_column_width=True)

        st.download_button(
            "Download result",
            data=response.content,
            file_name=f"{filter_name}_{uploaded_file.name}.png",
            mime="image/png",
        )
