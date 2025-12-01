"""
Custom Django fields for Codeteki CMS.
Includes WebP auto-conversion for uploaded images.
"""

import io
import os
from PIL import Image
from django.core.files.base import ContentFile
from django.db import models


def convert_to_webp(image_file, quality=85, max_size=None):
    """
    Convert an uploaded image to WebP format.

    Args:
        image_file: Django UploadedFile or similar file-like object
        quality: WebP compression quality (1-100, default 85)
        max_size: Optional tuple (width, height) to resize if larger

    Returns:
        ContentFile with WebP image data and new filename
    """
    # Open the image with Pillow
    img = Image.open(image_file)

    # Convert to RGB if necessary (WebP doesn't support all modes)
    if img.mode in ('RGBA', 'LA', 'P'):
        # Preserve transparency for RGBA/LA
        if img.mode == 'P':
            img = img.convert('RGBA')
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize if max_size is specified and image is larger
    if max_size:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Save to WebP format
    output = io.BytesIO()

    # Handle transparency
    if img.mode == 'RGBA':
        img.save(output, format='WEBP', quality=quality, lossless=False)
    else:
        img.save(output, format='WEBP', quality=quality, lossless=False)

    output.seek(0)

    # Generate new filename with .webp extension
    original_name = getattr(image_file, 'name', 'image.jpg')
    name_without_ext = os.path.splitext(original_name)[0]
    new_name = f"{name_without_ext}.webp"

    return ContentFile(output.read(), name=new_name)


class WebPImageField(models.ImageField):
    """
    Custom ImageField that automatically converts uploaded images to WebP format.

    Usage:
        class MyModel(models.Model):
            image = WebPImageField(upload_to='images/')

    Options:
        webp_quality: Compression quality (1-100, default 85)
        webp_max_size: Optional (width, height) tuple for max dimensions
        convert_to_webp: Set to False to disable conversion (default True)
    """

    def __init__(self, *args, webp_quality=85, webp_max_size=None, convert_to_webp=True, **kwargs):
        self.webp_quality = webp_quality
        self.webp_max_size = webp_max_size
        self.convert_to_webp_flag = convert_to_webp
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.webp_quality != 85:
            kwargs['webp_quality'] = self.webp_quality
        if self.webp_max_size is not None:
            kwargs['webp_max_size'] = self.webp_max_size
        if not self.convert_to_webp_flag:
            kwargs['convert_to_webp'] = self.convert_to_webp_flag
        return name, path, args, kwargs

    def pre_save(self, model_instance, add):
        file = getattr(model_instance, self.attname)

        if file and self.convert_to_webp_flag:
            # Check if it's a new upload (not already saved)
            if hasattr(file, 'file') and file.file:
                # Skip if already WebP
                if not file.name.lower().endswith('.webp'):
                    try:
                        # Reset file position
                        file.file.seek(0)

                        # Convert to WebP
                        webp_file = convert_to_webp(
                            file.file,
                            quality=self.webp_quality,
                            max_size=self.webp_max_size
                        )

                        # Update the file
                        file.save(webp_file.name, webp_file, save=False)
                    except Exception as e:
                        # If conversion fails, keep original image
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"WebP conversion failed for {file.name}: {e}")

        return super().pre_save(model_instance, add)


class OptimizedImageField(WebPImageField):
    """
    WebP ImageField with sensible defaults for web optimization.
    - Converts to WebP at 85% quality
    - Limits max dimension to 2000px (maintains aspect ratio)
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('webp_quality', 85)
        kwargs.setdefault('webp_max_size', (2000, 2000))
        super().__init__(*args, **kwargs)


class ThumbnailImageField(WebPImageField):
    """
    WebP ImageField optimized for thumbnails.
    - Converts to WebP at 80% quality
    - Limits max dimension to 800px
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('webp_quality', 80)
        kwargs.setdefault('webp_max_size', (800, 800))
        super().__init__(*args, **kwargs)
