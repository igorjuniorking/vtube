import os
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
from waitress import serve

app = Flask(__name__)

# Настройки папок
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# "База данных" в памяти (для примера)
videos = []

# --- HTML ШАБЛОН (YouTube Style) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PythonTube</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f0f0f; color: white; font-family: Roboto, Arial, sans-serif; }
        .navbar { background-color: #0f0f0f; border-bottom: 1px solid #333; }
        .card { background-color: transparent; border: none; transition: 0.3s; }
        .card-title { font-size: 1rem; font-weight: 500; margin-top: 10px; color: white; }
        .video-thumbnail { border-radius: 12px; width: 100%; aspect-ratio: 16/9; object-fit: cover; background: #222; }
        .upload-section { background: #1e1e1e; padding: 20px; border-radius: 15px; margin-bottom: 30px; }
        input, .form-control { background: #222 !important; border: 1px solid #444 !important; color: white !important; }
        .btn-primary { background-color: #cc0000; border: none; border-radius: 20px; padding: 8px 20px; }
        .btn-primary:hover { background-color: #ff0000; }
    </style>
</head>
<body>
    <nav class="navbar sticky-top mb-4">
        <div class="container-fluid">
            <a class="navbar-brand text-white fw-bold" href="/">🎬 PythonTube</a>
        </div>
    </nav>

    <div class="container">
        <div class="upload-section">
            <h5>Загрузить новое видео</h5>
            <form action="/upload" method="post" enctype="multipart/form-data" class="row g-3">
                <div class="col-md-5">
                    <input type="text" name="title" class="form-control" placeholder="Название видео" required>
                </div>
                <div class="col-md-5">
                    <input type="file" name="video" class="form-control" accept="video/*" required>
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-primary w-100">Опубликовать</button>
                </div>
            </form>
        </div>

        <h4 class="mb-4">Рекомендации</h4>
        <div class="row row-cols-1 row-cols-md-3 row-cols-lg-4 g-4">
            {% for video in videos %}
            <div class="col">
                <div class="card h-100">
                    <video class="video-thumbnail" controls>
                        <source src="/uploads/{{ video.filename }}" type="video/mp4">
                    </video>
                    <div class="card-body p-0">
                        <h5 class="card-title">{{ video.title }}</h5>
                        <p class="text-secondary small">Опубликовано только что</p>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

# --- МАРШРУТЫ (Routes) ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, videos=videos)

@app.route('/upload', methods=['POST'])
def upload():
    title = request.form.get('title')
    file = request.files.get('video')
    
    if file and title:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        videos.append({'title': title, 'filename': filename})
    
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- ЗАПУСК ЧЕРЕЗ WAITRESS ---
if __name__ == '__main__':
    print("🚀 Сервер запущен на http://localhost:8080")
    serve(app, host='0.0.0.0', port=8080)