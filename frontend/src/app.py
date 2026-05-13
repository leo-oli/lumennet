import os
import gradio as gr
from pathlib import Path
from client import LumenNetClient

# --- GLOBALS & CONFIG ---
SAMPLES_DIR = Path("samples")
api_client = LumenNetClient()


# --- EVENT HANDLER ---
def process_image(img):
    if img is None:
        raise gr.Error("Please upload an image first.")

    try:
        enhanced_pil = api_client.enhance(img)
        return (img, enhanced_pil)
    except Exception as e:
        raise gr.Error(str(e))


# --- DYNAMIC EXAMPLES ---
example_files = []
if SAMPLES_DIR.exists():
    example_files = [
        str(f)
        for f in SAMPLES_DIR.glob("*.*")
        if f.suffix.lower() in [".png", ".jpg", ".jpeg"]
    ]

# --- UI FRONTEND ---
with gr.Blocks(title="LumenNet AI") as app:
    gr.Markdown("# 🔦 LumenNet: Low-Light Enhancement")
    gr.Markdown(
        "Upload an underexposed image to recover hidden details and colors. | [View on GitHub](https://github.com/leo-oli/lumennet)"
    )

    with gr.Row():
        # make the upload column narrower and the result column wider
        with gr.Column(scale=1):
            input_image = gr.Image(type="pil", label="Upload Dark Image")
            enhance_btn = gr.Button("✨ Enhance Image", variant="primary")

        with gr.Column(scale=2):
            output_slider = gr.ImageSlider(
                label="Before / After", type="pil", buttons=["download"]
            )

    # wire the button
    enhance_btn.click(fn=process_image, inputs=input_image, outputs=output_slider)

    # built-in examples
    if example_files:
        gr.Markdown("### 🖼️ Try Examples")
        gr.Examples(
            examples=example_files,
            inputs=input_image,
            outputs=output_slider,
            fn=process_image,
            cache_examples=False,
        )
    else:
        gr.Markdown(
            f"*No examples found. Create a '{SAMPLES_DIR}' folder and add images to see them here.*"
        )

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("FRONTEND_PORT", 7860)),
        share=False,
    )
