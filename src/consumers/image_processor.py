from PIL import Image
from io import BytesIO

class ImageProcessor:
    def __init__(self, quality=85, output_format="JPEG"):
        self.quality = quality
        self.output_format = output_format

    def compress_image(self, input_path):
        """Compresse une image et retourne les données compressées."""
        image = Image.open(input_path)
        compressed_image = BytesIO()
        image.save(compressed_image, format=self.output_format, quality=self.quality)
        compressed_image.seek(0)
        return compressed_image.getvalue()

