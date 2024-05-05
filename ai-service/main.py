import logging
import os
import json

from clipsai import MediaEditor
from flask import Flask, request, jsonify, make_response, send_file, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from core.utils.clips import trim_clips, find_clips
from core.utils.azure import upload_clip_to_blob, download_blob_from_azure
from core.utils.common import get_random_clips
from core.contents.stt import STT



#TORCH COMMAND pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu118

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
CORS(app)
bcrypt = Bcrypt(app)
logging.basicConfig()

MEDIA_EDITOR = MediaEditor()

@app.route('/ai/get-clips', methods=['POST'])
def get_clips():
    data = request.get_json()

    filename = data.get('filename')
    choice = int(data.get('choice'))
    upload_id = data.get("upload_id")
    azure_conn_string = data.get("azure_conn_string")
    azure_container_name = data.get("azure_container_name")

    print(data)

    video_path = download_blob_from_azure(azure_conn_string, azure_container_name,filename,f"original_videos/{filename}")
    transcript_string, transcription_method, words, language = STT().get_transcript(video_path)
    print(language)
    detected_clips = find_clips(transcription_method,choice)
    rand_clips = get_random_clips(detected_clips)
    clips = trim_clips(rand_clips,video_path,transcript_string,MEDIA_EDITOR,words,upload_id)

    for clip in clips:
        upload_clip_to_blob(azure_conn_string, azure_container_name, clip["path"])
        os.remove(clip["path"])

    return {"clips" : clips, "language": language}

if __name__ == '__main__':
    app.run(port=8081)


