from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import io
from PIL import Image, UnidentifiedImageError
from .inference import load_model, enhance_image

# --- GLOBAL STATE ---
ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: load the model before the server starts accepting requests
    try:
        ml_models["session"] = load_model()
        print("Model loaded successfully")
    except Exception as e:
        ml_models["session"] = None
        print(f"Error loading model: {e}")
    yield
    # shutdown: clean up resources
    ml_models.clear()


# --- API CONFIG ---
app = FastAPI(
    title="LumenNet API",
    description="REST API for Low-Light Image Enhancement",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your frontend IP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- RESPONSE MODELS ---
class HealthCheckResponse(BaseModel):
    status: str
    message: str


# --- ENDPOINTS ---
@app.get(
    "/",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    tags=["System"],
)
def health_check():
    """Simple health check to verify the API is running and model is loaded"""
    if ml_models.get("session") is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API running, but ONNX model failed to load.",
        )
    return HealthCheckResponse(status="ok", message="LumenNet API is up and running")


@app.post(
    "/enhance",
    responses={
        status.HTTP_200_OK: {
            "content": {"image/png": {}},
            "description": "The enhanced image.",
        }
    },
    tags=["Enhancement"],
)
async def enhance_endpoint(file: UploadFile = File(...)):
    """
    Expects an image file upload, returns the enhanced image directly as a PNG binary stream
    """
    session = ml_models.get("session")
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model engine is currently unavailable.",
        )

    # validate file type via MIME
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid file type. Please upload an image",
        )

    try:
        # read the uploaded file bytes into a PIL Image
        image_bytes = await file.read()
        input_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The uploaded file is not a valid image",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading image: {str(e)}",
        )

    try:
        # run inference
        enhanced_image = enhance_image(input_image, session)

        # convert the resulting PIL Image back to bytes
        output_buffer = io.BytesIO()
        enhanced_image.save(output_buffer, format="PNG")
        output_bytes = output_buffer.getvalue()

        # return the image directly
        return Response(content=output_bytes, media_type="image/png")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image during inference: {str(e)}",
        )
