import streamlit as st
import os
import pandas as pd
from datetime import datetime

# Настройка страницы в стиле Wide (широкий экран)
st.set_page_config(page_title="StreamTube", page_icon="🎬", layout="wide")

# Создаем папку для хранения видео, если её нет
SAVE_DIR = "uploaded_videos"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Кастомный CSS для "YouTube" стиля
st.markdown("""
    <style>
    .main {
        background-color: #0f0f0f;
        color: white;
    }
    .stApp {
        background-color: #0f0f0f;
    }
    h1, h2, h3, p {
        color: white !important;
    }
    .video-card {
        background-color: #1e1e1e;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 20px;
        transition: 0.3s;
    }
    .video-card:hover {
        background-color: #2e2e2e;
    }
    .stSidebar {
        background-color: #0f0f0f !important;
        border-right: 1px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)

# Инициализация "базы данных" в сессии
if 'video_db' not in st.session_state:
    st.session_state.video_db = []

# --- САЙДБАР (Навигация и загрузка) ---
with st.sidebar:
    st.title("🎬 StreamTube")
    st.write("Твой личный видеохостинг")
    st.divider()
    
    st.subheader("Загрузить видео")
    new_title = st.text_input("Название видео", placeholder="Как я провел лето...")
    uploaded_file = st.file_uploader("Выберите файл", type=["mp4", "mov", "avi"])
    
    if st.button("Опубликовать", use_container_width=True):
        if uploaded_file and new_title:
            file_path = os.path.join(SAVE_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Добавляем в список
            st.session_state.video_db.append({
                "title": new_title,
                "path": file_path,
                "date": datetime.now().strftime("%d.%m.%Y")
            })
            st.success("Видео успешно загружено!")
        else:
            st.error("Введите название и выберите файл")

# --- ГЛАВНАЯ СТРАНИЦА ---
st.title("Рекомендации")

if not st.session_state.video_db:
    st.info("Пока здесь пусто. Загрузи первое видео через боковое меню! 👈")
else:
    # Отображение сеткой (Grid)
    cols = st.columns(3) # 3 колонки как на YouTube Desktop
    
    for idx, video in enumerate(st.session_state.video_db):
        with cols[idx % 3]:
            # Контейнер для видео
            with st.container():
                st.video(video['path'])
                st.subheader(video['title'])
                st.caption(f"📅 Опубликовано: {video['date']}")
                st.write("---")