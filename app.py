import sqlite3
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from moviepy.editor import VideoFileClip
from werkzeug.datastructures import FileStorage


app = Flask(__name__)

# App Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
app.config['DATABASE'] = 'videos.db'
app.config['API_TOKENS'] = {'abc', 'xyz'}
app.config['MIN_VIDEO_DURATION'] = 5  # seconds
app.config['MAX_VIDEO_DURATION'] = 11 # seconds

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def init_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE,
            size INTEGER,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db() # check database

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'mov', 'avi'}

def authenticate(token):
    return token in app.config['API_TOKENS']

@app.route('/upload', methods=['POST'])
def upload_video():
    token = request.headers.get('Authorization')
    if not token or not authenticate(token):
        return jsonify({'error': 'Authentication required'}), 401
    if 'video' not in request.files:
        return jsonify({'error': 'No video part'}), 400
    file: FileStorage = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        file_size = os.path.getsize(filepath)
        try:
            clip = VideoFileClip(filepath)
            duration = clip.duration
            clip.close()
            if not (app.config['MIN_VIDEO_DURATION'] <= duration <= app.config['MAX_VIDEO_DURATION']):
                os.remove(filepath)
                return jsonify({'error': f'Video duration must be between {app.config["MIN_VIDEO_DURATION"]} and {app.config["MAX_VIDEO_DURATION"]} seconds'}), 400
        except Exception as e:
            os.remove(filepath)
            return jsonify({'error': f'Error processing video: {str(e)}'}), 500

        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO videos (filename, size) VALUES (?, ?)", (filename, file_size))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            return jsonify({'error': f'File "{filename}" already exists'}), 409
        finally:
            conn.close()

        if file_size > app.config['MAX_CONTENT_LENGTH']:
            os.remove(filepath)
            return jsonify(
                {'error': f'Video size exceeds limit of {app.config["MAX_CONTENT_LENGTH"] / (1024 * 1024)} MB'}), 400

        return jsonify({'message': 'Video uploaded successfully', 'filename': filename}), 200
    else:
        return jsonify({'error': 'Allowed file types are mp4, mov, avi'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)