import os
import shutil
import tempfile
import zipfile
import base64
import re
import uuid
import traceback
from typing import List, Dict, Any, Optional, Union
from io import BytesIO
from uuid import uuid4
from pathlib import Path

import httpx
import aiofiles
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Image Title Generator API")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Please restrict appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API keys from environment variables
IOINTELLIGENCE_API_KEY = os.getenv("IOINTELLIGENCE_API_KEY")
# IO.NET API endpoint
IOINTELLIGENCE_API_ENDPOINT = os.getenv("IOINTELLIGENCE_API_ENDPOINT", "https://api.intelligence.io.solutions/api/v1/chat/completions")
# IO.NET Vision model
IOINTELLIGENCE_VISION_MODEL = os.getenv("IOINTELLIGENCE_VISION_MODEL", "meta-llama/Llama-3.2-90B-Vision-Instruct")

async def call_io_intelligence_api(data, api_purpose="general", timeout=60.0):
    """
    Generic function to call IO Intelligence API with proper error handling
    
    Args:
        data: The request payload
        api_purpose: String describing the purpose (for logging)
        timeout: Request timeout in seconds
        
    Returns:
        API response if successful, None otherwise
    """
    try:
        if not IOINTELLIGENCE_API_KEY:
            print(f"[ERROR] {api_purpose}: IO Intelligence API key is not set")
            raise ValueError("API key is missing")
            
        headers = {
            "Authorization": f"Bearer {IOINTELLIGENCE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Send async HTTP request with timeout
        try:
            print(f"[DEBUG] {api_purpose}: Sending request to {IOINTELLIGENCE_API_ENDPOINT}")
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    IOINTELLIGENCE_API_ENDPOINT,
                    headers=headers,
                    json=data,
                    timeout=timeout
                )
        except httpx.TimeoutException:
            print(f"[ERROR] {api_purpose}: Request timed out after {timeout} seconds")
            return None
            
        # Process response
        print(f"[DEBUG] {api_purpose}: API status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "choices" in result and result["choices"]:
                    return result
                else:
                    print(f"[ERROR] {api_purpose}: Response does not contain 'choices':", result)
            except Exception as e:
                print(f"[ERROR] {api_purpose}: JSON parsing failed: {e}")
                print(f"[DEBUG] {api_purpose}: Raw response: {response.text}")
        else:
            print(f"[ERROR] {api_purpose}: API response failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"[ERROR] {api_purpose}: Exception during API call: {e}")
        import traceback
        traceback.print_exc()
        
    return None

async def get_image_caption(image_path: str) -> str:
    """Get image caption using IO Intelligence API"""
    import base64

    try:
        print(f"[DEBUG] Starting caption generation: {image_path}")
        print(f"[DEBUG] API Endpoint: {IOINTELLIGENCE_API_ENDPOINT}")
        print(f"[DEBUG] Vision Model: {IOINTELLIGENCE_VISION_MODEL}")
        print(f"[DEBUG] API Key available: {bool(IOINTELLIGENCE_API_KEY)}")

        if not IOINTELLIGENCE_API_KEY:
            print("[ERROR] IO Intelligence API key is not set")
            raise ValueError("API key is missing")

        # Read image file as binary and encode to base64
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{base64_image}"

        # Prepare Vision API request data
        data = {
            "model": IOINTELLIGENCE_VISION_MODEL,
            "messages": [
                {"role": "system", "content": "You are an AI assistant."},
                {"role": "user", "content": [
                    {"type": "text", "text": "What is in this image?"},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]}
            ]
        }

        headers = {
            "Authorization": f"Bearer {IOINTELLIGENCE_API_KEY}",
            "Content-Type": "application/json"
        }

        # Send async HTTP request with increased timeout (60 seconds)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                print(f"[DEBUG] Sending request to: {IOINTELLIGENCE_API_ENDPOINT}")
                response = await client.post(
                    IOINTELLIGENCE_API_ENDPOINT,
                    headers=headers,
                    json=data,
                    timeout=60.0  # Explicit timeout
                )
        except httpx.TimeoutException:
            print("[ERROR] Request timed out after 60 seconds")
            raise ValueError("API request timed out")

        # Process response
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and result["choices"]:
                caption = result["choices"][0]["message"]["content"]
                print(f"[DEBUG] Caption retrieved successfully: {caption}")
                return caption
            else:
                print("[ERROR] Response does not contain caption:", result)
        else:
            print(f"[ERROR] API response failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"[ERROR] Exception while retrieving caption: {e}")

    # Fallback (if failed)
    file_name = os.path.basename(image_path)
    return f"An image with filename {file_name}"


def analyze_image_colors(img):
    """Analyze image colors and content to provide a simple description"""
    try:
        # Resize image to speed up processing
        img_small = img.resize((100, 100))
        # Convert RGBA to RGB if needed
        if img_small.mode == 'RGBA':
            img_small = img_small.convert('RGB')
            
        # Get average colors
        r, g, b = [sum(x) / len(x) for x in zip(*img_small.getdata())]
        
        # Get image size
        width, height = img.size
        
        # Calculate image hash (identifier based on content)
        import hashlib
        import io
        
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format)
        img_byte_arr = img_byte_arr.getvalue()
        
        # Calculate MD5 hash
        hash_obj = hashlib.md5(img_byte_arr)
        img_hash = hash_obj.hexdigest()
        print(f"[DEBUG] Image hash: {img_hash}")
        
        # Provide detailed description for specific known images
        # Register hash for test blue cat character images
        known_images = {
            # Add known image hashes and descriptions here
            # Example: "1a2b3c4d5e6f7g8h9i0j": "A blue cat character wearing a suit",
        }
        
        # Check image characteristics
        color_desc = ""
        if b > r * 1.5 and b > g * 1.5:
            color_desc = "bright blue"
        elif r > g * 1.5 and r > b * 1.5:
            color_desc = "predominantly red"
        elif g > r * 1.5 and g > b * 1.5:
            color_desc = "predominantly green"
        elif r > b and g > b and abs(r - g) < 30:
            color_desc = "yellowish"
        elif b > r and g > r and abs(b - g) < 30:
            color_desc = "cyan/teal colored"
        elif r > g and b > g and abs(r - b) < 30:
            color_desc = "purple/magenta colored"
        elif r > 200 and g > 200 and b > 200:
            color_desc = "very bright or white"
        elif r < 50 and g < 50 and b < 50:
            color_desc = "very dark or black"
        else:
            color_desc = "with mixed colors"
        
        return f"a {img.format.lower()} image that appears to be {color_desc}, size {width}x{height} pixels"
    except Exception as e:
        print(f"[ERROR] Color analysis error: {str(e)}")
        return "with various colors"

async def generate_title(caption: str, language: str) -> str:
    """Generate a title for an image caption using IO Intelligence API"""
    import re
    import uuid
    import traceback
    import os

    # Allowed image extensions
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

    def is_allowed_file(filename: str) -> bool:
        ext = os.path.splitext(filename)[1].lower()
        return ext in ALLOWED_EXTENSIONS

    print(f"[DEBUG] Starting title generation: caption=\"{caption}\", language={language}")
    print(f"[DEBUG] API Endpoint: {IOINTELLIGENCE_API_ENDPOINT}")
    print(f"[DEBUG] API Key available: {bool(IOINTELLIGENCE_API_KEY)}")

    try:
        if not IOINTELLIGENCE_API_KEY:
            print("[ERROR] IO Intelligence API key is not set")
            raise ValueError("API key is missing")

        # Trim caption if it's too long
        if len(caption) > 300:
            caption = caption[:300] + "..."
            print(f"[DEBUG] Trimmed caption: {caption}")

        prompt = f"Based on the following description, create an image title in {language} within 20 characters: {caption}\nPlease format your output exactly as follows:\n**Title:** \"title\""

        # Use IOINTELLIGENCE_VISION_MODEL instead of hardcoded model
        model_name = os.getenv("IOINTELLIGENCE_TITLE_MODEL", "deepseek-ai/DeepSeek-R1")
        print(f"[DEBUG] Using model for title generation: {model_name}")
        
        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are a naming assistant that generates short titles."},
                {"role": "user", "content": prompt}
            ]
        }

        headers = {
            "Authorization": f"Bearer {IOINTELLIGENCE_API_KEY}",
            "Content-Type": "application/json"
        }

        # Send async HTTP request with increased timeout (60 seconds)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                print(f"[DEBUG] Sending title request to: {IOINTELLIGENCE_API_ENDPOINT}")
                response = await client.post(
                    IOINTELLIGENCE_API_ENDPOINT,
                    headers=headers,
                    json=data,
                    timeout=60.0  # Explicit timeout
                )
        except httpx.TimeoutException:
            print("[ERROR] Title request timed out after 60 seconds")
            raise ValueError("Title API request timed out")

        print(f"[DEBUG] Title API status: {response.status_code}")
        print(f"[DEBUG] Title API headers: {response.headers}")
        print(f"[DEBUG] Title API response (raw): {response.text}")

        if response.status_code == 200:
            try:
                result = response.json()
                print(f"[DEBUG] Title API response (json): {result}")
            except Exception as e:
                print(f"[ERROR] JSON parsing failed: {e}")
                print(f"[DEBUG] Raw response text: {response.text}")
                traceback.print_exc()
                raise

            try:
                if "choices" in result and result["choices"]:
                    raw_title = result["choices"][0]["message"]["content"].strip()
                    print(f"[DEBUG] Title API response: {raw_title}")

                    match = re.search(r'\*\*Title:\*\*\s*\"([^\"]+)\"', raw_title)
                    if match:
                        extracted = match.group(1)
                        print(f"[DEBUG] Extracted title: {extracted}")
                    else:
                        extracted = raw_title.splitlines()[0]
                        print(f"[WARN] Title extraction failed, using first line: {extracted}")

                    sanitized_title = re.sub(r'[\\/:*?"<>|\s]', '_', extracted)
                    if len(sanitized_title) > 20:
                        sanitized_title = sanitized_title[:20]
                    return sanitized_title
                else:
                    print("[ERROR] Title generation response does not contain 'choices'")
            except Exception as inner_e:
                print(f"[ERROR] Exception while processing title response: {inner_e}")
                traceback.print_exc()
        else:
            print(f"[ERROR] Title generation API response failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"[ERROR] Exception during title generation: {e}")
        traceback.print_exc()

    fallback_title = f"image_{uuid.uuid4().hex[:8]}" if language == "en" else f"image_jp_{uuid.uuid4().hex[:8]}"
    return fallback_title



@app.post("/process-images")
async def process_images(
    files: List[UploadFile] = File(...),
    language: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Process image files, rename them and return as a ZIP file"""
    print(f"[DEBUG] Starting processing: {len(files)} files, language: {language}")
    
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
        
    if language not in ["en", "ja"]:
        raise HTTPException(status_code=400, detail="Invalid language. Use 'en' or 'ja'")
    
    # Create temporary directories
    temp_dir = tempfile.mkdtemp()
    output_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "renamed_images.zip")
    print(f"[DEBUG] Temporary directory: {temp_dir}, Output directory: {output_dir}")
    
    try:
        # Create ZIP file
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for i, file in enumerate(files):
                print(f"[DEBUG] Processing file {i+1}/{len(files)}: {file.filename}")
                
                # Get file extension
                _, ext = os.path.splitext(file.filename)
                
                # Save to temporary file
                temp_file_path = os.path.join(temp_dir, f"{uuid4()}{ext}")
                async with aiofiles.open(temp_file_path, 'wb') as f:
                    content = await file.read()
                    await f.write(content)
                
                # Get caption
                caption = await get_image_caption(temp_file_path)
                print(f"[DEBUG] Generated caption: {caption}")
                
                # Generate title
                title = await generate_title(caption, language)
                print(f"[DEBUG] Generated title: {title}")
                
                # Create new filename
                new_filename = f"{title}{ext}"
                renamed_path = os.path.join(output_dir, new_filename)
                print(f"[DEBUG] New filename: {new_filename}")
                
                # Copy and rename file
                shutil.copy2(temp_file_path, renamed_path)
                
                # Add to ZIP file
                zip_file.write(renamed_path, new_filename)
        
        # Cleanup function for background task
        def cleanup():
            print("[DEBUG] Starting temporary file cleanup")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir, ignore_errors=True)
            print("[DEBUG] Temporary file cleanup completed")
        
        # Register as background task
        from fastapi.concurrency import run_in_threadpool
        background_tasks.add_task(run_in_threadpool, cleanup)
        
        print(f"[DEBUG] Processing completed: ZIP created - {zip_path}")
        # Return ZIP file as response
        return FileResponse(
            zip_path,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=renamed_images.zip"},
            background=background_tasks
        )
    
    except Exception as e:
        print(f"[ERROR] Error during processing: {str(e)}")
        # Also clean up temp files if an error occurs
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Image Title Generator API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
