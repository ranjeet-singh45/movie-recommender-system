# 🎬 Movie Recommender System

A content-based movie recommendation web app built using **Streamlit**.  
Select a movie and get instant recommendations along with posters using TMDB API.

---

## 🚀 Live Demo
https://movie-recommender-system-feby7xtamrcrrfizbvyvjb.streamlit.app/
---

## 🧠 How It Works

- Combines movie metadata (genres, cast, crew, keywords) into a single feature
- Converts text into vectors using **CountVectorizer**
- Computes similarity using **Cosine Similarity**
- Recommends top 5 similar movies

---

## 🏗️ Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- TMDB API

---

## 📂 Project Structure
```
movie-recommender/
│
├── app.py
├── requirements.txt
├── model/
│ ├── movie_list.pkl
│ ├── similarity.pkl
|──data/
| |──tmdb_5000_credits.csv
| |──tmdb_5000_movies.csv

```
## ⚙️ Installation

### 1. Clone repository
```
git clone https://github.com/ranjeet-singh45/movie-recommender-system.git
cd movie-recommender-system
```
### 2. Create virtual environment (optional)
```
python -m venv venv
```
Activate:
- Windows:
```
venv\Scripts\activate
```
- Mac/Linux:
```
source venv/bin/activate
```
### 3. Install dependencies
```
pip install -r requirements.txt
```
### 4. Add API Key

Create `.env` file:
```
TMDB_API_KEY=your_api_key_here
```
### 5. Run the app
```
streamlit run app.py



