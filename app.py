import pickle
import streamlit as st
import requests
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

# API KEY
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
MOVIE_FILE_ID = "1ktKgENvp2l-9fEnLacmAqiFykoT-hHbW"
SIM_FILE_ID   = "1Rs2qoS_JdTH4b9d11SmGsIhYZrPE0vR6"

MODEL_DIR = "model"
MOVIE_PATH = f"{MODEL_DIR}/movie_list.pkl"
SIM_PATH = f"{MODEL_DIR}/similarity.pkl"

# -----------------------------
# DOWNLOAD FUNCTION
# -----------------------------
def download_file_from_drive(file_id, destination):
    URL = "https://drive.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={'id': file_id}, stream=True, timeout=30)

    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            response = session.get(
                URL,
                params={'id': file_id, 'confirm': value},
                stream=True,
                timeout=30
            )

    with open(destination, "wb") as f:
        for chunk in response.iter_content(1024 * 1024):
            if chunk:
                f.write(chunk)

# -----------------------------
# VALIDATE FILE
# -----------------------------
def is_valid_pickle(file_path):
    try:
        with open(file_path, "rb") as f:
            pickle.load(f)
        return True
    except:
        return False

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_resource
def load_data():
    os.makedirs(MODEL_DIR, exist_ok=True)

    # movie file
    if not os.path.exists(MOVIE_PATH) or not is_valid_pickle(MOVIE_PATH):
        if os.path.exists(MOVIE_PATH):
            os.remove(MOVIE_PATH)
        st.info("Downloading movie list...")
        download_file_from_drive(MOVIE_FILE_ID, MOVIE_PATH)

    # similarity file
    if not os.path.exists(SIM_PATH) or not is_valid_pickle(SIM_PATH):
        if os.path.exists(SIM_PATH):
            os.remove(SIM_PATH)
        st.info("Downloading similarity matrix (first run)...")
        download_file_from_drive(SIM_FILE_ID, SIM_PATH)

    # load
    movies = pickle.load(open(MOVIE_PATH, "rb"))
    similarity = pickle.load(open(SIM_PATH, "rb"))

    # ensure proper format
    if hasattr(similarity, "values"):
        similarity = similarity.values

    similarity = np.array(similarity)

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
        return "https://via.placeholder.com/500x750?text=No+Image"

    except:
        return "https://via.placeholder.com/500x750?text=Error"

# -----------------------------
# RECOMMEND FUNCTION (FINAL FIX)
# -----------------------------
def recommend(movie):
    if movie not in movies['title'].values:
        return [], []

    index = movies[movies['title'] == movie].index[0]

    # FIX HERE
    sim_scores = np.array(similarity[index]).flatten()
    st.write("Sample scores:", sim_scores[:10])

    distances = sorted(
        list(enumerate(sim_scores)),
        key=lambda x: x[1],
        reverse=True
    )

    names, posters = [], []

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