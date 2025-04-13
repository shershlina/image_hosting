import os
from urllib.parse import parse_qs
from uuid import uuid4

from loguru import logger

from AdvancedHandler import AdvancedHTTPRequestHandler
from DBManager import DBManager
from settings import IMAGES_FOLDER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE, ERROR_FILE


class ImageHostingHandler(AdvancedHTTPRequestHandler):
    server_version = "Image Hosting Server v0.2"

    def __init__(self, request, client_address, server):
        self.db = DBManager()
        super().__init__(request, client_address, server)

    def get_images(self):
        """Get list of images for gallery"""
        query_components = parse_qs(self.headers.get('Query-String'))
        page = int(query_components.get('page', ['1'])[0])
        if page < 1:
            page = 1
        images = self.db.get_images(page)
        images_json = []
        for image in images:
            image = {
                'filename': image[1],
                'original_name': image[2],
                'size': image[3],
                'upload_date': image[4].strftime('%Y-%m-%d %H:%M:%S'),
                'file_type': image[5]
            }
            images_json.append(image)

        self.send_json({
            'images': images_json
        })

    def post_upload(self):
        """Upload new image"""
        length = int(self.headers.get("Content-Length"))
        if length > MAX_FILE_SIZE:
            logger.warning("File too large")
            self.send_html(ERROR_FILE, 413)
            return

        data = self.rfile.read(length)
        orig_name, ext = os.path.splitext(self.headers.get("Filename"))
        filename = uuid4()
        if ext not in ALLOWED_EXTENSIONS:
            logger.warning("File type not allowed")
            self.send_html(ERROR_FILE, 400)
            return
        file_size_kb = round(length / 1024)
        self.db.add_image(filename, orig_name, file_size_kb, ext)
        with open(IMAGES_FOLDER + f"{filename}{ext}", "wb") as file:
            file.write(data)
        self.send_html("upload_success.html", headers={
            "Location": f"http://localhost/{IMAGES_FOLDER}{filename}{ext}"})

    def delete_image(self, image_id: str) -> None:
        """Deleting image"""
        logger.info(f'Try to delete image {image_id}')
        filename, ext = os.path.splitext(image_id)
        if not filename:
            logger.warning("Filename not found")
            self.send_html(ERROR_FILE, 404)
            return

        self.db.delete_image(filename)
        image_path = os.path.join(IMAGES_FOLDER, f'{filename}{ext}')
        if not os.path.exists(image_path):
            logger.warning("Image not found")
            self.send_html(ERROR_FILE, 404)

        os.remove(image_path)
        self.send_json({"Success": "Image deleted"})
