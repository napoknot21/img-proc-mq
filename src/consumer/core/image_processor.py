import os
from settings.config import *
from PIL import Image

def compress_image(file_path):
    """
    Compress an image and save it as a new file.

    Args:
        file_path (str): Path to the image to compress.

    Returns:
        str: Path to the compressed image file.

    Raises:
        RuntimeError: If the compression process fails.
    """
    try:

        with Image.open(file_path) as img:

            compressed_path = ROOT_STORAGE_FOLDER + DOWNLOAD_FOLDER + f"compressed_{os.path.basename(file_path)}"
            img = img.convert("RGB")
            img.save(compressed_path, "JPEG", optimize=True, quality=85)

            print(f"\n[+] Image compressed: {compressed_path}\n")
            return compressed_path

    except Exception as e:

        raise RuntimeError(f"[-] Failed to compress image: {e}")
