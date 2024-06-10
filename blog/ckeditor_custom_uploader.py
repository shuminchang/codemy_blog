from ckeditor_uploader.views import upload
from django.core.files.uploadedfile import UploadedFile
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.utils.translation import gettext as _
from PIL import Image, ExifTags
from io import BytesIO

def resize_image(image, max_width, max_height, max_size_kb):
    img = Image.open(image)

    # Correct image orientation using EXIF data if available
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = img._getexif()
        if exif is not None:
            orientation = exif.get(orientation)
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # No EXIF data; do nothing
        pass

    # Determine new size while maintaining aspect ratio
    if img.width > img.height:
        # Horizontal image
        target_width = max_width
        target_height = int(max_width * img.height / img.width)
    else:
        # Vertical image
        target_height = max_height
        target_width = int(max_height * img.width / img.height)

    img = img.resize((target_width, target_height), Image.LANCZOS)
    
    if img.mode in ("RGBA", "P"):  # Convert to RGB to remove transparency if present
        img = img.convert("RGB")

    # Reduce quality to fit in the size limit
    quality = 85
    while True:
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality)
        size_kb = buffer.tell() / 1024
        if size_kb <= max_size_kb or quality == 10:
            break
        quality -= 5

    return buffer.getvalue()

def custom_upload(request, *args, **kwargs):
    for file_key in request.FILES:
        uploaded_file = request.FILES[file_key]
        if isinstance(uploaded_file, UploadedFile):
            max_size_kb = 250  # 250 KB
            max_width, max_height = 800, 600

            image_data = resize_image(uploaded_file, max_width, max_height, max_size_kb)
            resized_file = ContentFile(image_data)
            resized_file.name = uploaded_file.name
            request.FILES[file_key] = resized_file

    return upload(request, *args, **kwargs)
