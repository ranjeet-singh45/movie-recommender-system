import pickle
import streamlit as st
import requests
import numpy as np
import os
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
# LOAD DATA
# -----------------------------
@st.cache_resource
def load_data():
    try:
        movies = pickle.load(open("model/movie_list.pkl", "rb"))
        similarity = pickle.load(open("model/similarity.pkl", "rb"))

        # ensure numpy array
        similarity = np.array(similarity)

        return movies, similarity

    except Exception as e:
        st.error(f"Error loading model files: {e}")
        st.stop()


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
# RECOMMEND FUNCTION
# -----------------------------
def recommend(movie):
    if movie not in movies['title'].values:
        return [], []

    index = movies[movies['title'] == movie].index[0]

    sim_scores = similarity[index]

    # ensure clean array
    sim_scores = np.array(sim_scores).flatten()

    # numpy sorting (stable)
    top_indices = np.argsort(sim_scores)[::-1][1:6]

    names, posters = [], []

    for i in top_indices:
        movie_id = movies.iloc[i].movie_id
        names.append(movies.iloc[i].title)
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