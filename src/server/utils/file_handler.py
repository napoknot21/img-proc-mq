import os
from werkzeug.utils import secure_filename

from config.config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER


def allowed_file (filename) :
    """
    Check if the file extension is allowed.
    Args:
        filename (str): The name of the file.
    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def save_file (file) :
    """
    Save the uploaded file to the specified upload folder.
    Args:
        file (FileStorage): The uploaded file.
    Returns:
        str: The file path where the file was saved.
    """
    try :
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        print(f"[+] File uploaded: {file_path}")
        return file_path

    except Exception as e :

        print(f"[-] Failed to save file: {e}")
        raise RuntimeError(f"Failed to save file: {e}")

