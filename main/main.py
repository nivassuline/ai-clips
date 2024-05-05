from flask import Flask, request, jsonify, make_response, send_file, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv

import logging
import requests
import os
import openai
import json

from core.utils.youtube import get_video
from core.utils.common import generate_random_string
from core.utils.azure import upload_clip_to_blob
from core.contents.chatgpt import get_gpt_clips

load_dotenv()


app = Flask(__name__)
app.logger.setLevel(logging.INFO)
CORS(app)
bcrypt = Bcrypt(app)
logging.basicConfig()

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
AZURE_CONN_STRING = os.environ.get('AZURE_CONN_STRING')
AZURE_CONTAINER_NAME = os.environ.get('AZURE_CONTAINER_NAME')
openai.api_key = os.environ.get('OPENAI_API_KEY')


@app.route('/api/get-ai-clips', methods=['GET'])
def get_ai_clips():
    url = request.args.get('url')
    choice = request.args.get('choice')
    upload_id = generate_random_string(16)
    filename = f"{upload_id}.mp4"

    local_path = get_video(url, filename)

    upload_clip_to_blob(AZURE_CONN_STRING, AZURE_CONTAINER_NAME,local_path)

    os.remove(local_path)

    # JSON data to be sent in the POST request
    json_data = {
    "filename": filename,
    "choice": choice,
    "upload_id": upload_id,
    "azure_conn_string": AZURE_CONN_STRING,
    "azure_container_name": AZURE_CONTAINER_NAME
    }

    # Make a POST request with JSON data
    response = requests.post(f"{os.environ.get('AI_SERVICE_URL')}/ai/get-clips", json=json_data)

    response_data = json.loads(response.content)

    print(response_data)

    clips = get_gpt_clips(openai, response_data["clips"], response_data["language"])

    print(clips)

    return response.json()



if __name__ == '__main__':
    app.run(port=8080)

