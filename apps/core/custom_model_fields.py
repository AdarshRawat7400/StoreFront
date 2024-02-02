from django.db import models
from django.core.files.base import ContentFile
import base64

class Base64Field(models.TextField):
    description = "A custom base64-encoded file field"

    def from_base64(self, value):
        try:
            decoded_data = base64.b64decode(value)
            return ContentFile(decoded_data)
        except Exception as e:
            # Handle decoding errors
            raise ValueError(f"Error decoding base64: {e}")

    def to_base64(self, file):
        try:
            return base64.b64encode(file.read()).decode('utf-8')
        except Exception as e:
            # Handle encoding errors
            raise ValueError(f"Error encoding to base64: {e}")

    def get_file(self, instance):
        base64_string = getattr(instance, self.attname)
        return self.from_base64(base64_string)
