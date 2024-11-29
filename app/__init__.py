import sqlite3
from flask import Flask, request, jsonify ,send_file ,render_template_string
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import uuid , random
from datetime import datetime, timedelta
import os
from moviepy.editor import VideoFileClip , concatenate_videoclips
# from flask_cors import CORS


app = Flask(__name__)
# CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024
app.config['MIN_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.config['DATABASE'] = 'videos.db'
app.config['API_TOKENS'] = {'abc', 'xyz'}
app.config['MIN_VIDEO_DURATION'] = 5
app.config['MAX_VIDEO_DURATION'] = 25


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def init_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS videos (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         filename TEXT UNIQUE,
    #         size INTEGER,
    #         upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    #         unique_id TEXT NOT NULL UNIQUE,
    # expiry_time TIMESTAMP NOT NULL
    #     )
    # ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                size INTEGER NOT NULL,
                unique_id TEXT NOT NULL UNIQUE,
                expiry_time TIMESTAMP NOT NULL
            );
        ''')
    conn.commit()
    conn.close()

init_db() #check database

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'mov', 'avi'}

def authenticate(token):
    return token in app.config['API_TOKENS']

@app.route('/')
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video Editor API</title>
    </head>
    <body>
        <h1>Video Editor API</h1>
        <p>The Video Editor API Client is a Python client designed to interact with a local Video Editor API, enabling users to perform operations such as uploading video files, merging multiple videos, and accessing individual video information based on unique identifiers.</p>
    </body>
    </html>
    """
    return render_template_string(html_content)

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

        # Check for minimum content length (5 MB)
        if file_size < app.config['MIN_CONTENT_LENGTH']:
            os.remove(filepath)
            return jsonify(
                {'error': f'Video size must be at least {app.config["MIN_CONTENT_LENGTH"] / (1024 * 1024)} MB'}), 400

        try:
            clip = VideoFileClip(filepath)
            duration = clip.duration
            clip.close()

            if not (app.config['MIN_VIDEO_DURATION'] <= duration <= app.config['MAX_VIDEO_DURATION']):
                os.remove(filepath)
                return jsonify({
                                   'error': f'Video duration must be between {app.config["MIN_VIDEO_DURATION"]} and {app.config["MAX_VIDEO_DURATION"]} seconds'}), 400

        except Exception as e:
            os.remove(filepath)
            return jsonify({'error': f'Error processing video: {str(e)}'}), 500
        unique_id = str(uuid.uuid4())
        expiry_time = datetime.now() + timedelta(hours=24)

        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO videos (filename, size, unique_id, expiry_time) VALUES (?, ?, ?, ?)", (filename, file_size,unique_id,expiry_time))
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
        shareable_link = f"{request.host_url}video/{unique_id}"
        return jsonify({'message': 'Video uploaded successfully', 'filename': filename,'shareable_link': shareable_link}), 200
    else:
        return jsonify({'error': 'Allowed file types are mp4, mov, avi'}), 400

@app.route('/merge', methods=['POST'])
def merge_videos():
    try:
        video_filenames = request.json.get('filenames')
        if not video_filenames or not isinstance(video_filenames, list):
            return jsonify({'error': 'Invalid filenames'}), 400

        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()

        # Check if filenames exist in the database
        cursor.execute("SELECT filename FROM videos WHERE filename IN ({})".format(",".join(["?"] * len(video_filenames))), video_filenames)
        db_filenames = [row[0] for row in cursor.fetchall()]

        if len(db_filenames) != len(video_filenames):
            conn.close()
            return jsonify({'error': 'One or more filenames not found in database'}), 404

        clips = []
        for filename in db_filenames:  # Use filenames from the database
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(filepath):  # Redundant check, but added for safety
                conn.close()
                return jsonify({'error': f'File "{filename}" not found'}), 404

            try:
                clip = VideoFileClip(filepath)
                clips.append(clip)
            except Exception as e:
                conn.close()
                return jsonify({'error': f'Error loading "{filename}": {str(e)}'}), 500

        conn.close()

        # Create the final merged video
        final_clip = concatenate_videoclips(clips)
        choice = random.randint(5, 100)
        merged_filename = "merged_video_" + str(choice) + ".mp4"
        merged_filepath = os.path.join(app.config['UPLOAD_FOLDER'], merged_filename)


        if os.path.exists(merged_filepath):
            return jsonify({'error': f'File "{merged_filename}" already exists on disk'}), 409

        final_clip.write_videofile(merged_filepath, codec='libx264')
        video_size = os.path.getsize(merged_filepath)  # Size in bytes
        for clip in clips:
            clip.close()
        final_clip.close()
        unique_id = str(uuid.uuid4())
        expiry_time = datetime.now() + timedelta(hours=24)
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO videos (filename, unique_id, expiry_time, size) VALUES (?, ?, ?, ?)",
                           (merged_filename, unique_id, expiry_time, video_size))
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            return jsonify({'error': f'Error saving to database for file "{merged_filename}": {str(e)}'}), 500
        finally:
            conn.close()

        shareable_link = f"{request.host_url}video/{unique_id}"
        return jsonify({'message': 'Videos merged successfully', 'filename': merged_filename,
                        'shareable_link': shareable_link}), 200

    except Exception as e:
        return jsonify({'error': f'Error merging videos: {str(e)}'}), 500

@app.route('/video/<unique_id>', methods=['GET'])
def access_video(unique_id):
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("SELECT filename, expiry_time FROM videos WHERE unique_id = ?", (unique_id,))
    video = cursor.fetchone()
    conn.close()

    if video is None:
        return jsonify({'error': 'Video not found'}), 404

    filename, expiry_time = video
    expiry_time = datetime.strptime(expiry_time, '%Y-%m-%d %H:%M:%S.%f')

    if datetime.now() > expiry_time:
        return jsonify({'error': 'Link has expired'}), 403

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'Video file not found'}), 404

    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
