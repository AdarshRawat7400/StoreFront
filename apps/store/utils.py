from django.utils.text import slugify
from .models import ProductImage
from django.core.files.uploadedfile import SimpleUploadedFile

def save_product_file(instance, uploaded_file, index):
    category_slug = slugify(instance.category.name)
    product_slug = slugify(instance.name)
    file_extension = uploaded_file.name.split('.')[-1]
    file_name = f"{category_slug}_{product_slug}_{index}.{file_extension}"

    # Save the resized image using ResizedImageField
    product_image = ProductImage(product=instance)
    # Save the resized image using ResizedImageField (delayed saving)
    product_image.image.save(file_name, SimpleUploadedFile(file_name, uploaded_file.read()), save=False)

    # Additional processing or handling of the file

    # Save the file permanently
    product_image.image.save(file_name, product_image.image, save=True)


    return product_image