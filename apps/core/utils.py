import os
import secrets
import string
import io
import base64
from PIL import Image
from django.core.files.base import ContentFile

from django.core.exceptions import ImproperlyConfigured


def get_env_var(var_name, default=None):
    try:
        return os.environ.get(var_name, default)
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)





def generate_random_password(length=12):
    """
    Generate a random password.

    :param length: Length of the password (default is 12)
    :return: Random password
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password




def convert_image_to_base64(image):
    """
    Convert PIL Image object to base64.

    Parameters:
        - image (PIL.Image.Image): PIL Image object.

    Returns:
        - str: Base64-encoded image string.
    """
    # Convert PIL Image object to base64
    with io.BytesIO() as buffer:
        image.save(buffer, format="PNG")  # Save as PNG, change format as needed
        base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return base64_image

def resize_image(image, desired_width, desired_height):
    """
    Resize a Pillow Image object to the specified width and height.

    Parameters:
        - image (PIL.Image.Image): Pillow Image object.
        - desired_width (int): Desired width of the resized image.
        - desired_height (int): Desired height of the resized image.

    Returns:
        - PIL.Image.Image: Resized Pillow Image object.
    """
    try:
        image = Image.open(image)
        # Calculate the aspect ratio of the original image
        aspect_ratio = image.width / image.height

        # Calculate the new height based on the desired width and aspect ratio
        new_height = int(desired_width / aspect_ratio)

        # Resize the image
        resized_image = image.resize((desired_width, new_height), Image.ANTIALIAS)
        
        # Crop the image to the desired height if needed
        if new_height > desired_height:
            top_crop = (new_height - desired_height) // 2
            bottom_crop = new_height - top_crop
            resized_image = resized_image.crop((0, top_crop, desired_width, bottom_crop))

        # Convert resized image to base64
        base64_resized_image = convert_image_to_base64(resized_image)

        return base64_resized_image

    except Exception as e:
        print(f"Error resizing image: {e}")
        return None
    


from PIL import Image
from django.core.files.uploadedfile import TemporaryUploadedFile

def convert_uploaded_file_to_webp(uploaded_file, output_name, resolution=(800, 600)):
    """
    Convert an uploaded file to WebP format with the specified resolution.

    Parameters:
    - uploaded_file (TemporaryUploadedFile): The uploaded file object.
    - output_name (str): The desired name for the output WebP image file.
    - resolution (tuple): Desired resolution (width, height). Default is (800, 600).

    Returns:
    - Image: The processed Image object.
    """
    try:
        # Open the uploaded file using Pillow
        with Image.open(uploaded_file) as img:
            # Resize the image to the specified resolution
            resized_img = img.resize(resolution, Image.ANTIALIAS)

            # Convert the Image object to bytes
            image_bytes = resized_img.tobytes()
            # Save the bytes to a ContentFile
            content_file = ContentFile(image_bytes)
            return content_file

    except Exception as e:
        print(f'Error converting image: {str(e)}')
        return None