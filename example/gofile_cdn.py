import os
import json
import psutil
from functools import wraps
from flask import Flask, request, jsonify, Response
from werkzeug.utils import secure_filename
from GoFile import GofileSyncClient

app = Flask("CDN Server")
SETTINGS_FILE = "settings.json"
upload_count = 0
client = GofileSyncClient()

def initialize_client():
    global client
    settings_path = os.path.join(os.getcwd(), SETTINGS_FILE)
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}
    if "token" not in settings:
        settings["token"] = client.register()
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    else:
        client.login(settings["token"])

def upload_counter(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global upload_count
        upload_count += 1
        return func(*args, **kwargs)
    return wrapper

def handle_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return wrapper

@app.route('/')
def index():
    return jsonify({
        "author": "zrpy",
        "backend": "gofile.io",
        "version": "1.0",
        "status": "active"
    })

@app.route('/uploads', methods=['GET'])
@handle_error
def list_folders():
    info = client.get_info(client.root_id)
    folders = info.get("children", {})
    folder_list = [folders[folder]["code"] for folder in folders]
    return jsonify({
        "folders": folder_list,
        "count": len(folder_list)
    })

@app.route('/uploads', methods=['POST'])
@upload_counter
@handle_error
def upload_files():
    files = request.files.getlist("files")
    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No files uploaded"}), 400
    folder = client.create_folder()
    file_list = []
    for file in files:
        if file.filename == '':
            continue
        file_name = secure_filename(file.filename)
        if not file_name:
            continue
        res = client.upload_by_content(file.read(), file_name, folder["id"])
        if "downloadPage" in res:
            file_list.append({
                "file_name": file_name,
                "file_id": res["id"],
                "folder_code": folder["name"]
            })
    return jsonify({
        "uploaded_files": file_list,
        "folder_code": folder["name"],
        "upload_count": len(file_list)
    })

@app.route('/uploads/<code>')
@handle_error
def get_folder_info(code):
    info = client.get_info(code)
    files = info.get("children", {})
    file_list = []
    for file_id, file_info in files.items():
        file_list.append({
            "file_name": file_info["name"],
            "file_id": file_info["id"],
            "url": f"/uploads/{code}/{file_info['id']}",
            "size": file_info.get("size", 0)
        })
    return jsonify({
        "files": file_list,
        "folder_code": code,
        "file_count": len(file_list)
    })

@app.route('/uploads/<code>/<file_id>')
@handle_error
def serve_file(code, file_id):
    info = client.get_info(code)
    contents = info.get("children", {})
    if file_id not in contents:
        return jsonify({"error": "File not found"}), 404
    file_info = contents[file_id]
    link = file_info["link"]
    response = client.session.get(link, headers=client._make_headers(client.token, True))
    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve file"}), 502
    content_type = response.headers.get("content-type", "application/octet-stream")
    return Response(
        response.content,
        content_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{file_info["name"]}"'
        }
    )

@app.route('/usage')
def usage_stats():
    memory_usage = psutil.virtual_memory().percent
    return jsonify({
        "storage_backend": "gofile.io",
        "memory_usage_percent": round(memory_usage, 2),
        "upload_count": upload_count,
        "status": "healthy" if memory_usage < 90 else "warning"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

if __name__ == "__main__":
    initialize_client()
    print("Starting CDN Server")
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False,
        threaded=True
    )
