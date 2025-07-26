import os
import yaml

from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# ---- Load config ----
with open("config.yaml") as f:
    cfg = yaml.safe_load(f)

server_cfg = cfg.get("server", {})

UPLOAD_FOLDER = server_cfg.get("upload_folder", "uploads")
DB_URI = server_cfg.get("database", "sqlite:///clipboard.db")
MAX_SIZE = server_cfg.get("max_upload_size_mb", 1) * 1024 * 1024 * 1024  # GB → bytes

# ---- Setup Flask ----
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_SIZE
db = SQLAlchemy(app)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -------- DB Model --------
class ClipboardEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))  # text or file
    content = db.Column(db.Text)
    device = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "device": self.device,
            "timestamp": self.timestamp.isoformat()
        }

# -------- ROUTES --------
@app.route('/')
def index():
    return "[s]-[s] Clipboard Server is Live"

@app.route('/send', methods=['POST'])
def send_clipboard():
    data = request.json
    if not all(k in data for k in ('type', 'content', 'device')):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    entry = ClipboardEntry(
        type=data['type'],
        content=data['content'],
        device=data['device']
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({"status": "saved", "id": entry.id})

@app.route('/get', methods=['GET'])
def get_clipboard():
    entry = ClipboardEntry.query.order_by(ClipboardEntry.timestamp.desc()).first()
    return jsonify(entry.to_dict()) if entry else jsonify({"status": "empty"})

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files.get('file')
    if uploaded_file:
        filename = uploaded_file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        uploaded_file.save(filepath)
        return jsonify({"status": "uploaded", "filename": filename})
    return jsonify({"status": "error", "message": "No file provided"}), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000)
