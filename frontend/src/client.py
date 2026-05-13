import os
import io
import httpx
from PIL import Image


class LumenNetClient:
    """Handles all HTTP communication with the LumenNet backend API"""

    def __init__(self):
        self.api_url = os.getenv("API_URL", "http://localhost:8000/enhance")

    def enhance(self, img: Image.Image) -> Image.Image:
        """Sends a PIL image to the API and returns the enhanced PIL image"""
        # convert the PIL Image to a byte stream
        with io.BytesIO() as img_byte_arr:
            img.save(img_byte_arr, format="PNG")
            img_bytes = img_byte_arr.getvalue()

        files = {"file": ("image.png", img_bytes, "image/png")}

        # send the request to the FastAPI backend
        try:
            response = httpx.post(self.api_url, files=files, timeout=30.0)

            # handle the response
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
            else:
                # try to extract the FastAPI error message if available
                error_detail = response.json().get("detail", response.text)
                raise RuntimeError(
                    f"API Error ({response.status_code}): {error_detail}"
                )

        except httpx.ConnectError:
            raise RuntimeError(f"Failed to connect to backend at {self.api_url}.")
        except httpx.TimeoutException:
            raise RuntimeError("The API request timed out.")
