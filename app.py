from flask import Flask, request, redirect, url_for, jsonify, render_template_string
from huggingface_hub import HfApi, HfFolder
import os
import json
import string
import random

app = Flask(__name__)

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
            try:
                token = get_random_token()
                dataset_id = get_random_dataset()
                HfFolder.save_token(token)
                api = HfApi()
                upload_to_hf(api, file, new_filename, dataset_id)  # Pass the file object directly
                hf_url = f"https://huggingface.co/datasets/{dataset_id}/resolve/main/{new_filename}"
                custom_url = f"https://file.upload.duongkum999.me/{new_filename}"
                save_url_to_json(hf_url)
                return redirect(url_for('index', file_url=custom_url))
            except Exception as e:
                return f"An error occurred: {str(e)}"
    
    file_url = request.args.get('file_url')
    return render_template_string(HTML_TEMPLATE, file_url=file_url)

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
        try:
            token = get_random_token()
            dataset_id = get_random_dataset()
            HfFolder.save_token(token)
            api = HfApi()
            upload_to_hf(api, file, new_filename, dataset_id)  # Pass the file object directly
            hf_url = f"https://huggingface.co/datasets/{dataset_id}/resolve/main/{new_filename}"
            custom_url = f"https://file.upload.duongkum999.me/{new_filename}"
            save_url_to_json(hf_url)
            return jsonify({"url": custom_url}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def upload_to_hf(api, file_obj, filename, dataset_id):
    api.upload_file(
        path_or_fileobj=file_obj.stream,  # Use the stream of the file object
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

# HTML template as a string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload files, share them easily</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background-color: #f3e5ab;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
        }
        .upload-container {
            text-align: center;
            border: 2px dashed #333;
            border-radius: 10px;
            padding: 40px;
            width: 50%;
            max-width: 600px;
            background: rgba(255, 255, 255, 0.8);
            transition: background-color 0.3s ease;
        }
        .upload-container:hover,
        .upload-container.dragover {
            background: rgba(255, 255, 255, 0.9);
        }
        .upload-container h1 {
            margin-bottom: 20px;
            font-size: 24px;
        }
        .upload-container p {
            font-size: 16px;
        }
        .upload-container input[type="file"] {
            display: none;
        }
        .upload-container label {
            color: #fff;
            background-color: #007bff;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 20px;
            display: inline-block;
        }
        .upload-container button {
            margin-left: 10px;
            padding: 10px 20px;
            background-color: #28a745;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .link-container {
            margin-top: 20px;
            padding: 10px;
            background: #fff;
            border: 1px solid #ccc;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .link-container input[type="text"] {
            width: 80%;
            border: none;
            outline: none;
        }
        .link-container button.copy-button {
            padding: 5px 10px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>

<div class="upload-container" id="upload-container">
    <h1>Upload files, share them easily</h1>
    <p>Click here or drag & drop files to upload or transfer</p>
    <form id="upload-form" action="/" method="post" enctype="multipart/form-data">
        <label for="file-input">Choose Files</label>
        <input type="file" name="file" id="file-input" multiple>
        <button type="submit">Upload</button>
    </form>
    <div id="link-container" class="link-container">
        {% if file_url %}
            <input type="text" id="file-link" value="{{ file_url }}" readonly>
            <button class="copy-button" onclick="copyLink()">Copy Link</button>
        {% endif %}
    </div>
</div>

<script>
    function copyLink() {
        const link = document.getElementById("file-link");
        link.select();
        link.setSelectionRange(0, 99999); 
        document.execCommand("copy");
        alert("Copied the link: " + link.value);
    }

    if (window.location.search.includes("file_url=")) {
        const url = new URL(window.location);
        url.searchParams.delete("file_url");
        window.history.replaceState({}, document.title, url.pathname);
    }

    const uploadContainer = document.getElementById('upload-container');
    const fileInput = document.getElementById('file-input');

    uploadContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadContainer.classList.add('dragover');
    });

    uploadContainer.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadContainer.classList.remove('dragover');
    });

    uploadContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadContainer.classList.remove('dragover');
        fileInput.files = e.dataTransfer.files;
        document.getElementById('upload-form').submit();
    });
</script>

</body>
</html>
"""

# Main entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8787, debug=True)
