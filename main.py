from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import yt_dlp

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set output_path to the root directory of the project
output_path = os.path.dirname(os.path.abspath(__file__))
os.makedirs(output_path, exist_ok=True)


def delete_file(file_path: str):
    os.remove(file_path)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/download")
async def download_video(request: Request, background_tasks: BackgroundTasks):
    url = request.query_params.get('url')
    if not url:
        return {"error": "URL parameter is required"}

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'cookiefile': 'cookies.txt',  # Path to your cookies file
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)

        if not os.path.exists(file_path):
            return {"error": "File not found"}

        response = FileResponse(file_path, media_type='video/mp4', filename=os.path.basename(file_path))
        background_tasks.add_task(delete_file, file_path)
        return response
    except Exception as e:
        print(f"Something went wrong: {e}")
        return {"error": "Something went wrong"}