import os
from pathlib import Path, PurePath
from urllib.parse import urlparse

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

BASE_DIR = Path(__file__).parent

gauth = GoogleAuth()
drive = GoogleDrive(gauth)


# upload_file_list = [r'C:\Users\luiz_\projects\bot_cotacao\images\full\sodimac\1790_ARGAMASSA.jpg',]
# for upload_file in upload_file_list:
#     gfile = drive.CreateFile({'parents': [{'id': '1pzschX3uMbxU0lB5WZ6IlEEeAUE8MZ-t'}]})
#     # Read file and set it as the content of this instance.
#     gfile.SetContentFile(upload_file)
#     gfile.Upload()  # Upload the file.

SERVICE_ACCOUNT_FILE = r'C:\Users\luiz_\zeta360\envio_smss_clientes_bazar_gf\GF-Message-Logs-With-GSheets-bdce94b7c3d8.json'

file_path = PurePath(BASE_DIR, SERVICE_ACCOUNT_FILE)


def extract_image_info(image_url):
    # image_name, image_extension = os.path.splitext(os.path.basename(image_url))
    # os.path.basename(urlparse(image_url).path)
    image_name, image_extension = os.path.splitext(os.path.basename(urlparse(image_url).path))
    return image_name, image_extension
