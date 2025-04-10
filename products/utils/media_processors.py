import os
import subprocess
import tempfile
import uuid
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

def process_video(video_file, bitrate='4500k'):
    """
    Process video file to standardize bitrate using H.264 codec
    
    Args:
        video_file: The Django uploaded file object
        bitrate: Target bitrate (default 4500k)
    
    Returns:
        Processed file path
    """
    try:
        temp_dir = tempfile.gettempdir()
        input_filename = f"{uuid.uuid4()}_input{os.path.splitext(video_file.name)[1]}"
        output_filename = f"{uuid.uuid4()}_output.mp4"
        input_path = os.path.join(temp_dir, input_filename)
        output_path = os.path.join(temp_dir, output_filename)
        
        with open(input_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
        duration = None
        try:
            duration_cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                input_path
            ]
            duration_result = subprocess.run(
                duration_cmd,
                check=True,
                capture_output=True,
                text=True
            )
            duration = int(float(duration_result.stdout.strip()))
        except Exception as e:
            logger.error(f"Error extracting video duration: {e}")
        command = [
            'ffmpeg',
            '-y',
            '-i', input_path,
            '-c:v', 'libx264', 
            '-b:v', bitrate,
            '-preset', 'medium', 
            '-profile:v', 'main',
            '-level', '4.0',     
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',       
            '-b:a', '128k',      
            '-movflags', '+faststart', 
            output_path
        ]
        
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True
        )
        
        with open(output_path, 'rb') as processed_file:
            content = processed_file.read()
            
        os.remove(input_path)
        os.remove(output_path)
        
        return ContentFile(content, name=os.path.basename(video_file.name))
    
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        logger.error(f"FFmpeg error output: {e}")
        return video_file

def process_product_image(image_file):
    """
    Process product image to make it 1:1 aspect ratio by cropping
    
    Args:
        image_file: The Django uploaded file object
    
    Returns:
        Processed file with 1:1 aspect ratio
    """
    try:
        img = Image.open(image_file)
        
        width, height = img.size
        
        size = min(width, height)
        
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        
        cropped_img = img.crop((left, top, right, bottom))
        
        output = io.BytesIO()

        format = os.path.splitext(image_file.name)[1][1:].upper()
        if format == 'JPG':
            format = 'JPEG'
        
        if format not in ['JPEG', 'PNG', 'GIF', 'WEBP']:
            format = 'JPEG'
        
        cropped_img.save(output, format=format, quality=90)
        output.seek(0)
        
        return ContentFile(output.getvalue(), name=image_file.name)
    
    except Exception as e:
        logger.error(f"Error processing product image: {e}")
        return image_file 

def process_banner_image(image_file, target_width=1280, target_height=720):
    """
    Process banner image to 1280x720 resolution while maintaining aspect ratio
    
    Args:
        image_file: The Django uploaded file object
        target_width: Target width (default 1280)
        target_height: Target height (default 720)
    
    Returns:
        Processed file with 1280x720 resolution
    """
    try:
        img = Image.open(image_file)
        print("hello trying this out")
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            new_width = int(img.height * target_ratio)
            resized_img = img.resize((int(new_width * (target_height / img.height)), target_height), Image.LANCZOS)
            left = (resized_img.width - target_width) // 2
            top = 0
            right = left + target_width
            bottom = target_height
            cropped_img = resized_img.crop((left, top, right, bottom))
        else:
            new_height = int(img.width / target_ratio)
            resized_img = img.resize((target_width, int(new_height * (target_width / img.width))), Image.LANCZOS)
            left = 0
            top = (resized_img.height - target_height) // 2
            right = target_width
            bottom = top + target_height
            cropped_img = resized_img.crop((left, top, right, bottom))
        
        output = io.BytesIO()
        
        format = os.path.splitext(image_file.name)[1][1:].upper()
        if format == 'JPG':
            format = 'JPEG'
        
        if format not in ['JPEG', 'PNG', 'GIF', 'WEBP']:
            format = 'JPEG'
        
        cropped_img.save(output, format=format, quality=90)
        output.seek(0)
        
        return ContentFile(output.getvalue(), name=image_file.name)
    
    except Exception as e:
        logger.error(f"Error processing banner image: {e}")
        return image_file