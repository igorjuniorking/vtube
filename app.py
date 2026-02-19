import os
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, jsonify
from waitress import serve

app = Flask(__name__)

# Папка для видео
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Список видео (в реальном приложении лучше использовать БД типа SQLite)
videos = []

# --- HTML ШАБЛОН ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PythonTube Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f0f0f; color: white; font-family: 'Roboto', sans-serif; }
        .navbar { background-color: #0f0f0f; border-bottom: 1px solid #333; padding: 15px; }
        .video-card { background-color: #1e1e1e; border-radius: 12px; overflow: hidden; height: 100%; border: 1px solid #333; }
        .video-thumb { width: 100%; aspect-ratio: 16/9; background: #000; }
        .upload-area { background: #1e1e1e; border: 2px dashed #444; border-radius: 15px; padding: 25px; margin-bottom: 40px; }
        .progress { height: 10px; background-color: #333; display: none; margin-top: 15px; }
        .progress-bar { background-color: #cc0000; }
        .btn-delete { color: #aaa; text-decoration: none; font-size: 0.8rem; transition: 0.3s; }
        .btn-delete:hover { color: #ff4d4d; }
        input, .form-control { background: #2c2c2c !important; border: 1px solid #444 !important; color: white !important; }
    </style>
</head>
<body>
    <nav class="navbar mb-4">
        <div class="container text-center">
            <a class="navbar-brand text-white fw-bold" href="/">🎬 PYTUBE PREMIUM</a>
        </div>
    </nav>

    <div class="container">
        <div class="upload-area">
            <h5 class="mb-3">Новое видео</h5>
            <form id="uploadForm">
                <div class="row g-2">
                    <div class="col-md-5">
                        <input type="text" id="videoTitle" class="form-control" placeholder="Название..." required>
                    </div>
                    <div class="col-md-5">
                        <input type="file" id="videoFile" class="form-control" accept="video/*" required>
                    </div>
                    <div class="col-md-2">
                        <button type="submit" class="btn btn-danger w-100 fw-bold">ЗАГРУЗИТЬ</button>
                    </div>
                </div>
                <div class="progress" id="progressWrapper">
                    <div id="progressBar" class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%"></div>
                </div>
                <div id="statusText" class="small mt-2 text-secondary text-center"></div>
            </form>
        </div>

        <div class="row row-cols-1 row-cols-md-3 g-4" id="videoGrid">
            {% for video in videos %}
            <div class="col" id="vid-{{ loop.index0 }}">
                <div class="video-card">
                    <video class="video-thumb" controls>
                        <source src="/uploads/{{ video.filename }}" type="video/mp4">
                    </video>
                    <div class="p-3 d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1">{{ video.title }}</h6>
                            <small class="text-secondary">Файл: {{ video.filename }}</small>
                        </div>
                        <a href="/delete/{{ loop.index0 }}" class="btn-delete">Удалить</a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        const uploadForm = document.getElementById('uploadForm');
        const progressBar = document.getElementById('progressBar');
        const progressWrapper = document.getElementById('progressWrapper');
        const statusText = document.getElementById('statusText');

        uploadForm.onsubmit = function(e) {
            e.preventDefault();
            
            const file = document.getElementById('videoFile').files[0];
            const title = document.getElementById('videoTitle').value;
            const formData = new FormData();
            formData.append('video', file);
            formData.append('title', title);

            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/upload', true);

            // Показываем прогресс-бар
            progressWrapper.style.display = 'flex';

            xhr.upload.onprogress = function(e) {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    progressBar.style.width = percentComplete + '%';
                    statusText.innerText = 'Загружено: ' + Math.round(percentComplete) + '%';
                }
            };

            xhr.onload = function() {
                if (xhr.status === 200) {
                    window.location.reload(); // Перезагружаем, чтобы увидеть видео
                } else {
                    alert('Ошибка при загрузке');
                }
            };

            xhr.send(formData);
        };
    </script>
</body>
</html>
"""

# --- ЛОГИКА ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, videos=videos)

@app.route('/upload', methods=['POST'])
def upload():
    title = request.form.get('title')
    file = request.files.get('video')
    
    if file and title:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        videos.append({'title': title, 'filename': filename})
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/delete/<int:video_id>')
def delete(video_id):
    if 0 <= video_id < len(videos):
        video = videos.pop(video_id)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], video['filename'])
        if os.path.exists(file_path):
            os.remove(file_path)
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print("🚀 Сервер запущен на http://localhost:8080")
    # Используем Waitress
    serve(app, host='0.0.0.0', port=8080)