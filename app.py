import cgi
import json
import os
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
from os.path import isfile, join, splitext

from PIL import Image
from loguru import logger

UPLOAD_FOLDER = "images"
STATIC_FOLDER = "static"
SERVER_ADDRESS = ('0.0.0.0', 8000)
LOG_FILE = "logs/app.log"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}
MAX_FILE_SIZE = (5 * 1024 * 1024)

logger.add(LOG_FILE, format="[{time: YYYY-MM-DD HH:mm:ss}] | {level} | {message}")


class ImageHostingHandler(BaseHTTPRequestHandler):
    server_version = "Image Hosting Server, ver. 0.1"

    def __init__(self, request, client_address, server):
        self.get_routes = {
            "/upload": self.get_upload,
            "/images": self.get_images
        }
        self.post_routes = {
            "/upload": self.post_upload,
        }
        super().__init__(request, client_address, server)

    def do_GET(self):
        if self.path in self.get_routes:
            self.get_routes[self.path]()
        else:
            logger.warning(f"GET 404 {self.path}")
            self.send_response(404, "Not Found")

    def do_POST(self):
        if self.path in self.post_routes:
            self.post_routes[self.path]()
        else:
            logger.warning(f"POST {self.path}")
            self.send_response(405, "Method Not Allowed")

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        SimpleHTTPRequestHandler.end_headers(self)

    def get_images(self):
        logger.info(f"GET {self.path}")

        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.end_headers()

        images = [file for file in os.listdir(UPLOAD_FOLDER) if isfile(join("images", file))]
        self.wfile.write(json.dumps({"images": images}).encode("utf-8"))

    def get_upload(self):
        logger.info(f"GET {self.path}")
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(open("upload.html", "rb").read())

    def post_upload(self):
        logger.info(f"POST {self.path}")
        content_length = int(self.headers.get("Content-Length"))
        if content_length > MAX_FILE_SIZE:
            logger.error("Payload Too Large")
            self.send_response(413, "Payload Too Large")
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={"REQUEST_METHOD": "POST"}
        )
        data = form["image"].file

        _, ext = splitext(form["image"].filename)

        if ext not in ALLOWED_EXTENSIONS:
            logger.error("File type not allowed")
            self.send_response(400, "File type not allowed")
            return

        image_id = uuid.uuid4()
        image_name = f"{image_id}{ext}"
        with open(f"{UPLOAD_FOLDER}/{image_name}", "wb") as f:
            f.write(data.read())

        try:
            im = Image.open(f'{UPLOAD_FOLDER}/{image_name}')
            im.verify()
        except (IOError, SyntaxError) as e:
            logger.error(f'Invalid file: {e}')
            self.send_response(400, 'Invalid file')
            return

        logger.info(f"Upload success: {image_id}{ext}")
        self.send_response(301)
        self.send_header("Location", f"/images/{image_id}{ext}")
        self.end_headers()


def run():
    httpd = HTTPServer(SERVER_ADDRESS, ImageHostingHandler)
    try:
        logger.info(f"Serving at http://{SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}")
        httpd.serve_forever()
    except Exception:
        pass
    finally:
        logger.info("Server stopped")
        httpd.server_close()


if __name__ == "__main__":
    run()
