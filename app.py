from flask import Flask, request, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
import os
import uuid
from mxlTOnames import process_file

ALLOWED_EXTENSIONS = {"mxl", "musicxml", "xml"}
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    # Serve the existing `index.html` in the project folder
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if not allowed_file(file.filename):
        return "Unsupported file extension", 400

    # Save file with a unique prefix to avoid collisions
    original_filename = secure_filename(file.filename)
    unique_prefix = uuid.uuid4().hex
    save_filename = f"{unique_prefix}_{original_filename}"
    save_path = os.path.join(UPLOAD_FOLDER, save_filename)
    file.save(save_path)

    try:
        annotated_path = process_file(save_path, output_dir=UPLOAD_FOLDER)
    except Exception as e:
        # Clean up uploaded file on failure
        try:
            os.remove(save_path)
        except Exception:
            pass
        return (str(e), 500)

    annotated_basename = os.path.basename(annotated_path)
    file_url = f"/files/{annotated_basename}"

    return jsonify({"file_url": file_url})


@app.route('/files/<path:filename>')
def serve_file(filename):
    # Security: ensure path is inside upload folder
    safe_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(safe_path):
        abort(404)
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    # Use 0.0.0.0 for accessibility or 127.0.0.1 for local only
    app.run(host='127.0.0.1', port=5000, debug=True)
