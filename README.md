### *Project image_hosting*
A web service for viewing and storing images. Users upload images via the website and receive direct links to them. 
Users also can see the gallery of uploaded images with previews.

### *Supported formats:* 
.jpg, .jpeg, .png, .gif

### *Max file size:*
5 MB

### *How to run the project*

```bash
docker compose up --build
```
The application will be available at: `http://localhost:8080`

### *Routes*
- **Route:** `/`
The project’s homepage with a welcome message. Contains links to key routes.
- **Route:** `/upload`
Accepts an image file via HTTP POST request. 
Saves the image to the server’s `/images` folder and returns a page with a direct link to the uploaded file.
- **Route:** `/images`
Uploaded images gallery displaying:
  - Preview of each image
  - Direct link to the full image
  - File size
  - Upload date and time
  - Delete button for each image
- **Route:** `/images/<имя_файла>`
Direct access to specific uploaded image for viewing/downloading.

### *Architecture*
Two main components:
1. **Python backend:**
   - Handles HTTP requests processing, image uploads, data validation and logging
   - Implements application business logic for managing uploaded files
   - Runs in a Docker container listening on port `8000`
   - Built without frameworks using only Python's standard library (`http.server`)

2. **Nginx-сервер:**
   - Serves static files and uploaded images via the `/images/` route
   - Proxies requests to Python backend for other routes
   - Runs in a separate Docker container listening on port `80`

Components communicate through a local network created with Docker Compose.

### *Dependencies*
- Docker
- Python >= 3.12
- loguru
- psycopg
- dotenv