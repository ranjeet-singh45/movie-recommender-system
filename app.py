import pickle
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# -----------------------------
# LOAD ENV VARIABLES
# -----------------------------
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

# Stop app if API key missing
if not API_KEY:
    st.error("TMDB API key not found. Please set TMDB_API_KEY in .env file.")
    st.stop()


# -----------------------------
# FETCH POSTER (CACHED)
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

    except Exception:
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

    recommended_names = []
    recommended_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_names.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_names, recommended_posters


# -----------------------------
# LOAD DATA (CACHED)
# -----------------------------
@st.cache_resource
def load_data():
    try:
        movies = pickle.load(open("model/movie_list.pkl", "rb"))
        similarity = pickle.load(open("model/similarity.pkl", "rb"))
        return movies, similarity
    except Exception as e:
        st.error(f"Error loading model files: {e}")
        st.stop()


movies, similarity = load_data()


# -----------------------------
# UI
# -----------------------------
st.title("🎬 Movie Recommender System")

movie_list = movies['title'].values

selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
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