import os

from gradio_app import build_app

demo = build_app()

if __name__ == "__main__":
    demo.launch(
        server_name=os.getenv("GRADIO_HOST", "0.0.0.0"),
        server_port=int(os.getenv("GRADIO_PORT", "7860")),
    )
