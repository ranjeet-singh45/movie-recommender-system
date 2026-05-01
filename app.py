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

# Use Streamlit secrets (for deployment)
try:
    API_KEY = st.secrets["TMDB_API_KEY"]
except:
    API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    st.error("TMDB API key not found. Set it in Streamlit secrets or .env")
    st.stop()

# -----------------------------
# GOOGLE DRIVE FILE IDs
# -----------------------------
MOVIE_FILE_ID = "18bxKN-IaMxpzx_jNkMRtYXCMTaFWH6Up"
SIM_FILE_ID = "1jHsO9L9jfPH4XNrQeYagzwyzNcIHLv7F"

MODEL_DIR = "model"
MOVIE_PATH = f"{MODEL_DIR}/movie_list.pkl"
SIM_PATH = f"{MODEL_DIR}/similarity.pkl"

# -----------------------------
# DOWNLOAD FUNCTION
# -----------------------------
def download_file_from_drive(file_id, destination):
    url = f"https://drive.google.com/uc?id={file_id}"
    response = requests.get(url)

    if response.status_code != 200:
        st.error("Failed to download model files.")
        st.stop()

    with open(destination, "wb") as f:
        f.write(response.content)

# -----------------------------
# LOAD DATA (WITH AUTO DOWNLOAD)
# -----------------------------
@st.cache_resource
def load_data():
    os.makedirs(MODEL_DIR, exist_ok=True)

    if not os.path.exists(MOVIE_PATH):
        st.info("Downloading movie list...")
        download_file_from_drive(MOVIE_FILE_ID, MOVIE_PATH)

    if not os.path.exists(SIM_PATH):
        st.info("Downloading similarity matrix (first run only)...")
        download_file_from_drive(SIM_FILE_ID, SIM_PATH)

    movies = pickle.load(open(MOVIE_PATH, "rb"))
    similarity = pickle.load(open(SIM_PATH, "rb"))

    return movies, similarity


movies, similarity = load_data()

# -----------------------------
# FETCH POSTER
# -----------------------------
@st.cache_data
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return "https://via.placeholder.com/500x750?text=API+Error"

        data = response.json()
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
    "Type or select a movie from the dropdown",
    movies['title'].values
)

if st.button("Show Recommendation"):
    names, posters = recommend(selected_movie)

    if not names:
        st.warning("Movie not found in database.")
    else:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i])