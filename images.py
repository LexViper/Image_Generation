import gradio as gr
import requests
import io
from PIL import Image
import base64
import numpy as np
import time
import random
import os
from urllib.parse import urlparse

# HuggingFace Inference API (Free tier with limitations)
# Note: You need to create a free HuggingFace account to get an API token
# Visit: https://huggingface.co/settings/tokens

def generate_image_huggingface(api_token, prompt, style="none"):
    """
    Generate an image based on a text prompt using HuggingFace's free Inference API.
    
    Parameters:
    - api_token: Your HuggingFace API token
    - prompt: Description of the image to generate
    - style: Style preset to apply
    """
    if not api_token.strip():
        return None, "Error: Please enter your HuggingFace API token"
    
    if not prompt.strip():
        return None, "Error: Please enter a prompt"
    
    # Apply style modifications to prompt
    if style != "none":
        style_prompts = {
            "anime": ", anime style, anime art, japanese animation style, vibrant colors, clean lines",
            "ghibli": ", Studio Ghibli style, Miyazaki inspired, hand-drawn animation, painterly, whimsical, detailed background, fantasy elements",
            "photographic": ", professional photography, photorealistic, detailed, sharp focus, high resolution photograph",
            "digital-art": ", digital art, digital painting, detailed, vibrant colors, smooth gradients, 8k resolution",
            "comic-book": ", comic book style, bold outlines, flat colors, action-oriented, dynamic composition",
            "fantasy-art": ", fantasy art, magical, ethereal, mystical atmosphere, detailed, vibrant colors",
            "line-art": ", line art, black and white, minimal, clean lines, no shading",
            "cinematic": ", cinematic, dramatic lighting, movie still, film grain, wide angle, dramatic composition"
        }
        prompt = prompt + style_prompts.get(style, "")
    
    # HuggingFace models for image generation (free tier)
    models = [
        "stabilityai/stable-diffusion-xl-base-1.0",
        "runwayml/stable-diffusion-v1-5",
        "prompthero/openjourney"
    ]
    
    # Try different models if one fails
    for model in models:
        try:
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            
            # Check if rate limited
            if response.status_code == 429:
                # Try waiting if rate limited
                time.sleep(5)
                response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                return image, f"Success! Image generated using {model}"
            
        except Exception as e:
            continue
    
    return None, "Error: All models failed to generate an image. Please try again later."

def analyze_image_and_generate_prompt(api_token, input_image):
    """
    Analyze an image and generate a prompt using HuggingFace's free Inference API.
    
    Parameters:
    - api_token: Your HuggingFace API token
    - input_image: The source image to analyze
    """
    if not api_token.strip():
        return "Error: Please enter your HuggingFace API token"
    
    if input_image is None:
        return "Error: Please upload an image"
    
    # Convert image to bytes
    image_bytes = io.BytesIO()
    input_image.save(image_bytes, format='JPEG')
    image_bytes = image_bytes.getvalue()
    
    # Try different image captioning models
    models = [
        "Salesforce/blip-image-captioning-large",
        "nlpconnect/vit-gpt2-image-captioning"
    ]
    
    for model in models:
        try:
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            
            headers = {
                "Authorization": f"Bearer {api_token}"
            }
            
            response = requests.post(
                api_url,
                headers=headers,
                data=image_bytes,
                timeout=60
            )
            
            # Check if rate limited
            if response.status_code == 429:
                time.sleep(5)
                response = requests.post(api_url, headers=headers, data=image_bytes, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # Different models return different formats
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], dict) and "generated_text" in result[0]:
                        caption = result[0]["generated_text"]
                    else:
                        caption = result[0]
                elif isinstance(result, dict) and "generated_text" in result:
                    caption = result["generated_text"]
                else:
                    caption = str(result)
                
                # Enhance the prompt
                enhanced_prompt = enhance_prompt(caption)
                return enhanced_prompt
                
        except Exception as e:
            continue
    
    # If all API calls fail, fall back to local analysis
    return generate_fallback_prompt(input_image)

def enhance_prompt(caption):
    """Enhance a basic caption with additional descriptive elements."""
    enhancements = [
        "highly detailed",
        "professional quality",
        "sharp focus",
        "intricate details",
        "beautiful composition",
        "stunning",
        "high resolution",
        "masterpiece"
    ]
    
    # Add 2-3 random enhancements
    selected_enhancements = random.sample(enhancements, random.randint(2, 3))
    enhanced_caption = f"{caption}, {', '.join(selected_enhancements)}"
    
    return enhanced_caption

def generate_fallback_prompt(image):
    """
    Generate a basic prompt from an image when API fails.
    Uses simple image analysis to create a description.
    """
    # Convert to small size for analysis
    img = image.copy()
    img.thumbnail((100, 100))
    
    # Simple color analysis
    colors = img.getcolors(10000)
    if colors:
        colors.sort(reverse=True, key=lambda x: x[0])
        dominant_colors = colors[:3]
        
        # Map RGB to basic color names
        color_names = []
        for count, (r, g, b) in dominant_colors:
            if r > 200 and g > 200 and b > 200:
                color_names.append("white")
            elif r < 60 and g < 60 and b < 60:
                color_names.append("black")
            elif r > 200 and g < 100 and b < 100:
                color_names.append("red")
            elif r < 100 and g > 200 and b < 100:
                color_names.append("green")
            elif r < 100 and g < 100 and b > 200:
                color_names.append("blue")
            elif r > 200 and g > 200 and b < 100:
                color_names.append("yellow")
            else:
                color_names.append("colorful")
        
        color_desc = " and ".join(list(set(color_names))[:2])
    else:
        color_desc = "colorful"
    
    # Brightness analysis
    brightness = sum(img.convert("L").getdata()) / (img.width * img.height)
    if brightness > 200:
        light_desc = "bright"
    elif brightness < 50:
        light_desc = "dark"
    else:
        light_desc = "balanced"
    
    # Aspect ratio for scene type guessing
    aspect = img.width / img.height
    if aspect > 1.2:
        scene_type = "landscape"
    elif aspect < 0.8:
        scene_type = "portrait"
    else:
        scene_type = "scene"
    
    # Random adjectives to enrich description
    adjectives = ["detailed", "beautiful", "stunning", "professional", "high-quality", 
                  "artistic", "creative", "impressive", "elegant", "dynamic"]
    
    # Generate prompt
    prompt = f"A {random.choice(adjectives)} {light_desc} {scene_type} with {color_desc} elements, highly detailed, professional photography, sharp focus, high resolution"
    
    return prompt

def download_image_from_url(url):
    """
    Download an image from a URL and return a PIL Image object.
    Returns None if download fails.
    """
    try:
        # Extract filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        # Download the image
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        return None
    except:
        return None

# Create Gradio interface
with gr.Blocks(title="Free Style Image Generator") as app:
    gr.Markdown("# Free Style Image Generator")
    gr.Markdown("This app uses HuggingFace's free Inference API for image generation and analysis.")
    
    with gr.Tabs():
        with gr.TabItem("Text to Image"):
            with gr.Row():
                with gr.Column():
                    api_token = gr.Textbox(
                        label="HuggingFace API Token", 
                        placeholder="Enter your HuggingFace API token",
                        type="password",
                        info="Get a free token at huggingface.co/settings/tokens"
                    )
                    prompt_txt = gr.Textbox(
                        label="Prompt", 
                        placeholder="Describe the image you want to generate",
                        lines=3
                    )
                    style_txt = gr.Dropdown(
                        choices=["none", "ghibli", "anime", "photographic", "digital-art", "comic-book", "fantasy-art", "line-art", "cinematic"],
                        value="none",
                        label="Style Preset"
                    )
                    generate_btn = gr.Button("Generate Image", variant="primary")
                    
                with gr.Column():
                    output_image = gr.Image(label="Generated Image")
                    output_message = gr.Textbox(label="Status")
            
            # Add some examples
            gr.Examples(
                examples=[
                    ["A peaceful countryside with a small cottage"],
                    ["A young girl with a cat in a magical forest"],
                    ["A floating castle in the sky with airships"],
                    ["A quiet riverside town at sunset"],
                ],
                inputs=prompt_txt
            )
            
        with gr.TabItem("Image to Prompt"):
            with gr.Row():
                with gr.Column():
                    api_token_prompt = gr.Textbox(
                        label="HuggingFace API Token", 
                        placeholder="Enter your HuggingFace API token",
                        type="password",
                        info="Get a free token at huggingface.co/settings/tokens"
                    )
                    
                    with gr.Tabs():
                        with gr.TabItem("Upload Image"):
                            input_image = gr.Image(
                                label="Upload Image to Generate Prompt", 
                                type="pil"
                            )
                        
                        with gr.TabItem("Image URL"):
                            image_url = gr.Textbox(
                                label="Image URL",
                                placeholder="Enter URL of an image"
                            )
                            fetch_image_btn = gr.Button("Fetch Image")
                    
                    analyze_btn = gr.Button("Analyze Image & Generate Prompt", variant="primary")
                    generated_prompt = gr.Textbox(
                        label="Generated Prompt", 
                        lines=4,
                        placeholder="Your detailed prompt will appear here..."
                    )
                    use_prompt_btn = gr.Button("Use this Prompt to Generate New Image")
                    style_prompt = gr.Dropdown(
                        choices=["none", "ghibli", "anime", "photographic", "digital-art", "comic-book", "fantasy-art", "line-art", "cinematic"],
                        value="none",
                        label="Style for New Image"
                    )
                
                with gr.Column():
                   
                    output_image_prompt = gr.Image(label="Generated Image")
                    output_message_prompt = gr.Textbox(label="Status")
    
    # Add information about API and limitations
    gr.Markdown("""
    ## Instructions:
    1. Get a free HuggingFace API token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
    2. Enter your token in the API Token field
    3. Enter a prompt or upload an image
    
    ## Features:
    - **Text to Image**: Create images from your text descriptions
    - **Image to Prompt**: Upload an image to get a detailed prompt, then use that prompt to generate new styled images
    - **Multiple Style Options**: Choose from various artistic styles
    
    ## Note:
    - This uses the free tier of HuggingFace's API which has rate limits
    - If you encounter "Rate limit exceeded" errors, wait a few minutes before trying again
    - The API token is only used to make requests and is not stored
    """)
    
    # Connect the buttons to functions
    generate_btn.click(
        fn=generate_image_huggingface,
        inputs=[api_token, prompt_txt, style_txt],
        outputs=[output_image, output_message]
    )
    
    def fetch_and_display_image(url):
        if not url.strip():
            return None, "Please enter a valid URL"
        
        image = download_image_from_url(url)
        if image is None:
            return None, "Failed to download image from URL"
        
        return image, "Image fetched successfully"
    
    fetch_image_btn.click(
        fn=fetch_and_display_image,
        inputs=[image_url],
        outputs=[ output_message_prompt]
    )
    
    def analyze_from_interface(api_token, uploaded_image, displayed_image):
        # Use whichever image is available
        image_to_analyze = uploaded_image if uploaded_image is not None else displayed_image
        
        if image_to_analyze is None:
            return "Please upload an image or fetch from URL first"
        
        return analyze_image_and_generate_prompt(api_token, image_to_analyze)
    
    analyze_btn.click(
        fn=analyze_from_interface,
        inputs=[api_token_prompt, input_image, ],
        outputs=generated_prompt
    )
    
    use_prompt_btn.click(
        fn=generate_image_huggingface,
        inputs=[api_token_prompt, generated_prompt, style_prompt],
        outputs=[output_image_prompt, output_message_prompt]
    )

# Launch the app
if __name__ == "__main__":
    app.launch()