import os
from http.server import HTTPServer

from dotenv import load_dotenv
from loguru import logger

from DBManager import DBManager
from ImageHostingHandler import ImageHostingHandler
from Router import Router
from routes import register_routes
from settings import SERVER_ADDRESS, LOG_PATH, LOG_FILE


def run(server_class=HTTPServer, handler_class=ImageHostingHandler):
    load_dotenv()
    logger.add(os.path.join(LOG_PATH, LOG_FILE),
               format="[{time: YYYY-MM-DD HH:mm:ss}] | {level} | {message}",
               level="INFO")

    db = DBManager(os.getenv('POSTGRES_DB'),
                   os.getenv('POSTGRES_USER'),
                   os.getenv('POSTGRES_PASSWORD'),
                   os.getenv('POSTGRES_HOST'),
                   os.getenv('POSTGRES_PORT'))
    db.init_tables()

    router = Router()
    register_routes(router, handler_class)

    httpd = server_class(SERVER_ADDRESS, handler_class)
    logger.info(f"Serving at http://{SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt, server stopped")
        httpd.server_close()
    finally:
        logger.info("Server stopped")


if __name__ == "__main__":
    run()
