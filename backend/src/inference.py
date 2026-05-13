import onnxruntime as ort
import numpy as np
from PIL import Image
from pathlib import Path

# --- GLOBALS ---
MODEL_PATH = Path("models/lumennet.onnx")


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")

    # load ONNX model optimized for CPU
    return ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])


def enhance_image(img_pil: Image.Image, session: ort.InferenceSession) -> Image.Image:
    # convert to [0, 1] float32 array
    img_np = np.array(img_pil.convert("RGB"), dtype=np.float32) / 255.0
    H, W = img_np.shape[:2]

    # pad to nearest multiple of 32
    pad_h = (32 - H % 32) % 32
    pad_w = (32 - W % 32) % 32
    img_padded = np.pad(img_np, ((0, pad_h), (0, pad_w), (0, 0)), mode="reflect")

    # transpose to [C, H, W] and add Batch Dimension
    input_tensor = np.expand_dims(img_padded.transpose(2, 0, 1), axis=0)

    # ONNX pnference
    input_name = session.get_inputs()[0].name
    out_tensor = session.run(None, {input_name: input_tensor})[0][0]

    # post-processing
    out_tensor = out_tensor[:, :H, :W]
    out_img = np.clip(out_tensor.transpose(1, 2, 0), 0.0, 1.0)

    return Image.fromarray((out_img * 255).astype(np.uint8))
