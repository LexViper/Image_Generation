import os
import io
import base64
import requests
from PIL import Image
from dotenv import load_dotenv
import gradio as gr

# Load environment variables
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("STABILITY_API_KEY")

# Function to generate a Ghibli-style image from a text prompt
def generate_ghibli_image(prompt):
    # Check if API key is available
    if not API_KEY:
        return None, "No API key found. Make sure you have a .env file with STABILITY_API_KEY=your_key"

    enhanced_prompt = f"{prompt}, Studio Ghibli style, Hayao Miyazaki, hand-drawn animation, soft colors, dreamy atmosphere, whimsical"
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "text_prompts": [
            {"text": enhanced_prompt, "weight": 1.0}
        ],
        "cfg_scale": 7,
        "height": 1024,  # Changed to 1024
        "width": 1024,   # Changed to 1024
        "samples": 1,
        "steps": 30,
        "style_preset": "anime"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            return None, f"Error: {response.status_code} - {response.json().get('message', 'Unknown error')}"

        data = response.json()
        if "artifacts" not in data or len(data["artifacts"]) == 0:
            return None, "Error: No image generated"

        image_b64 = data["artifacts"][0]["base64"]
        image_data = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_data))
        return image, "Image generated successfully!"
    except Exception as e:
        return None, f"An error occurred: {str(e)}"

# Gradio Interface
def interface(prompt):
    image, status = generate_ghibli_image(prompt)
    return image, status

iface = gr.Interface(fn=interface, inputs="text", outputs=["image", "text"], title="Ghibli Image Generator", description="Generate Ghibli-style images from your text prompt!")
iface.launch()


