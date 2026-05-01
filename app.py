import pickle
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

# API KEY (cloud + local)
try:
    API_KEY = st.secrets["TMDB_API_KEY"]
except:
    API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    st.error("TMDB API key not found.")
    st.stop()

# -----------------------------
# GOOGLE DRIVE FILE IDs
# -----------------------------
MOVIE_FILE_ID = "18bxKN-IaMxpzx_jNkMRtYXCMTaFWH6Up"
SIM_FILE_ID   = "1jHsO9L9jfPH4XNrQeYagzwyzNcIHLv7F"

MODEL_DIR = "model"
MOVIE_PATH = f"{MODEL_DIR}/movie_list.pkl"
SIM_PATH = f"{MODEL_DIR}/similarity.pkl"

# -----------------------------
# DOWNLOAD FUNCTION (ROBUST)
# -----------------------------
def download_file_from_drive(file_id, destination):
    URL = "https://drive.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={'id': file_id}, stream=True)

    # Handle Google Drive confirmation for large files
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            response = session.get(
                URL,
                params={'id': file_id, 'confirm': value},
                stream=True
            )

    with open(destination, "wb") as f:
        for chunk in response.iter_content(1024 * 1024):
            if chunk:
                f.write(chunk)

# -----------------------------
# VALIDATE FILE (IMPORTANT)
# -----------------------------
def is_valid_pickle(file_path):
    try:
        with open(file_path, "rb") as f:
            header = f.read(2)
            return header != b'<!'  # HTML check
    except:
        return False

# -----------------------------
# LOAD DATA (AUTO DOWNLOAD + FIX)
# -----------------------------
@st.cache_resource
def load_data():
    os.makedirs(MODEL_DIR, exist_ok=True)

    # MOVIE FILE
    if not os.path.exists(MOVIE_PATH) or not is_valid_pickle(MOVIE_PATH):
        st.warning("Downloading / fixing movie list...")
        if os.path.exists(MOVIE_PATH):
            os.remove(MOVIE_PATH)
        download_file_from_drive(MOVIE_FILE_ID, MOVIE_PATH)

    # SIMILARITY FILE
    if not os.path.exists(SIM_PATH) or not is_valid_pickle(SIM_PATH):
        st.warning("Downloading / fixing similarity matrix (first run only)...")
        if os.path.exists(SIM_PATH):
            os.remove(SIM_PATH)
        download_file_from_drive(SIM_FILE_ID, SIM_PATH)

    # LOAD
    try:
        movies = pickle.load(open(MOVIE_PATH, "rb"))
        similarity = pickle.load(open(SIM_PATH, "rb"))
    except Exception as e:
        st.error("Model files are corrupted. Please redeploy.")
        st.stop()

    return movies, similarity


movies, similarity = load_data()

# -----------------------------
# FETCH POSTER
# -----------------------------
@st.cache_data
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        data = requests.get(url, timeout=5).json()

        poster_path = data.get("poster_path")

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"

    except:
        return "https://via.placeholder.com/500x750?text=Error"

# -----------------------------
# RECOMMEND FUNCTION
# -----------------------------
def recommend(movie):
    if movie not in movies['title'].values:
        return [], []

    index = movies[movies['title'] == movie].index[0]

    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    names = []
    posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))

    return names, posters

# -----------------------------
# UI
# -----------------------------
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox(
    "Select a movie",
    movies['title'].values
)

if st.button("Show Recommendation"):
    names, posters = recommend(selected_movie)

    if not names:
        st.warning("Movie not found.")
    else:
        cols = st.columns(5)

        for i in range(len(names)):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i])