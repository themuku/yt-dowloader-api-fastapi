from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import FileResponse
import os
import yt_dlp

app = FastAPI()

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
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