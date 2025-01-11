import os
from PIL import Image

def compress_image(file_path):
    """Compresse une image et retourne le chemin du fichier compressé."""
    try:

        with Image.open(file_path) as img:
            compressed_path = f"./downloads/compressed_{os.path.basename(file_path)}"
            img = img.convert("RGB")  # Convertir en RGB si nécessaire
            img.save(compressed_path, "JPEG", optimize=True, quality=85)
            print(f"[+] Image compressed: {compressed_path}")
            return compressed_path

    except Exception as e:
        raise RuntimeError(f"[-]Failed to compress image: {e}")
