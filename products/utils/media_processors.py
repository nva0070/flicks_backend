import os
import subprocess
import tempfile
import logging
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

def process_video(video_file):
    """
    Process video using ffmpeg:
    1. Get video duration
    2. Compress video to 4500 kbps bitrate
    3. Normalize audio
    
    Returns: (processed_video, duration_in_seconds)
    """
    if not video_file:
        return video_file, None
        
    try:
        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as input_file:
            for chunk in video_file.chunks():
                input_file.write(chunk)
            input_path = input_file.name
            
        output_path = input_path + '_processed.mp4'
        
        # Get video duration
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
        
        # Process video with ffmpeg - compress to 4500 kbps bitrate
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'libx264',     # Use H.264 codec
            '-b:v', '4500k',       # Set video bitrate to 4500 kbps
            '-maxrate', '5000k',   # Maximum bitrate
            '-bufsize', '8000k',   # Buffer size
            '-c:a', 'aac',         # Use AAC for audio
            '-b:a', '192k',        # Audio bitrate
            '-ar', '48000',        # Audio sample rate
            '-af', 'loudnorm',     # Normalize audio
            '-movflags', '+faststart', # Optimize for web streaming
            '-y',                  # Overwrite output files
            output_path
        ]
        
        # Run the ffmpeg command
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Read the processed file
        with open(output_path, 'rb') as f:
            processed_content = f.read()
        
        # Create a ContentFile with the processed video
        filename = os.path.basename(video_file.name)
        processed_file = ContentFile(processed_content, name=filename)
        
        # Clean up temporary files
        os.unlink(input_path)
        os.unlink(output_path)
        
        return processed_file, duration
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        return video_file, duration  # Return original file if processing fails

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