from flask import Flask, request, render_template, redirect, url_for, jsonify
from huggingface_hub import HfApi, HfFolder
import os
import json
import string
import random

app = Flask(__name__)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
HUGGING_FACE_TOKENS = [
    "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",
    "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",
    "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",
    "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",
    "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"
]
DATASET_IDS = [
    "dunbot/filetempapi2",
    "dunbot/filetempapi"
]
URL_JSON_FILE = 'url.json'
def generate_random_filename(extension):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"{random_string}{extension}"
def get_random_token():
    return random.choice(HUGGING_FACE_TOKENS)
def get_random_dataset():
    return random.choice(DATASET_IDS)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            original_extension = os.path.splitext(file.filename)[1]  
            new_filename = generate_random_filename(original_extension)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            file.save(file_path)
            try:
                token = get_random_token()
                dataset_id = get_random_dataset()
                HfFolder.save_token(token)
                api = HfApi()
                upload_to_hf(api, file_path, new_filename, dataset_id)
                hf_url = f"https://huggingface.co/datasets/{dataset_id}/resolve/main/{new_filename}"
                custom_url = f"https://file.upload.duongkum999.me/{new_filename}"
                save_url_to_json(hf_url)
                os.remove(file_path)
                return redirect(url_for('index', file_url=custom_url))
            except Exception as e:
                return f"An error occurred: {str(e)}"    
    file_url = request.args.get('file_url')
    return render_template('index.html', file_url=file_url)
@app.route('/api/upload', methods=['POST'])
def api_upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        original_extension = os.path.splitext(file.filename)[1] 
        new_filename = generate_random_filename(original_extension)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(file_path)
        try:
            token = get_random_token()
            dataset_id = get_random_dataset()
            HfFolder.save_token(token)
            api = HfApi()
            upload_to_hf(api, file_path, new_filename, dataset_id)
            hf_url = f"https://huggingface.co/datasets/{dataset_id}/resolve/main/{new_filename}"
            custom_url = f"https://file.upload.duongkum999.me/{new_filename}"
            save_url_to_json(hf_url)
            os.remove(file_path)            
            return jsonify({"url": custom_url}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def upload_to_hf(api, file_path, filename, dataset_id):
    with open(file_path, "rb") as f:
        api.upload_file(
            path_or_fileobj=f,
            path_in_repo=filename,
            repo_id=dataset_id,
            repo_type="dataset"
        )
def save_url_to_json(url):
    if os.path.exists(URL_JSON_FILE):
        with open(URL_JSON_FILE, 'r') as file:
            data = json.load(file)
    else:
        data = []    
    data.append(url)    
    with open(URL_JSON_FILE, 'w') as file:
        json.dump(data, file, indent=2)
if __name__ == '__main__':
    app.run(debug=True)
