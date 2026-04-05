import streamlit as st
import pickle
import pandas as pd
import requests

# Load pickle files
user_movie_matrix_filled = pickle.load(open('user_movie_matrix_filled.pkl', 'rb'))
ratings_mean_count = pickle.load(open('ratings_mean_count.pkl', 'rb'))
movies_list = pickle.load(open('movies_list.pkl', 'rb'))

# TMDB API Key
API_KEY = st.secrets["TMDB_API_KEY"]

# Page config
st.set_page_config(page_title="Movie Recommender System", page_icon="🎬", layout="wide")

# Title
st.title("🎬 Movie Recommender System")
st.markdown("Discover movies you will love based on what you already enjoy!")

# Fetch poster function
def fetch_poster(movie_title):
    try:
        clean_title = movie_title.split('(')[0].strip()
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={clean_title}"
        response = requests.get(url)
        data = response.json()
        if data['results']:
            poster_path = data['results'][0]['poster_path']
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"

# Fix movie name function
def fix_name(movie):
    name = movie.split('(')[0].strip()
    if ', The' in name:
        name = 'The ' + name.replace(', The', '')
    elif ', A' in name:
        name = 'A ' + name.replace(', A', '')
    elif ', An' in name:
        name = 'An ' + name.replace(', An', '')
    return name

# Featured movies to show on dashboard
featured_movies = [
    "Forrest Gump (1994)",
    "Shawshank Redemption, The (1994)",
    "Dark Knight, The (2008)",
    "Inception (2010)",
    "Pulp Fiction (1994)",
    "Matrix, The (1999)",
    "Fight Club (1999)",
    "Interstellar (2014)"
]

# Show featured movies section
st.markdown("---")
st.subheader("🔥 Popular Movies")
cols = st.columns(8)
for i, movie in enumerate(featured_movies):
    with cols[i]:
        poster = fetch_poster(movie)
        st.image(poster, use_column_width=True)
        st.caption(f"**{fix_name(movie)}**")

st.markdown("---")

# Recommend function
def recommend(movie_name):
    movie_ratings = user_movie_matrix_filled[movie_name]
    similar = user_movie_matrix_filled.corrwith(movie_ratings)
    corr_df = pd.DataFrame(similar, columns=['correlation'])
    corr_df.dropna(inplace=True)
    corr_df = corr_df.join(ratings_mean_count['count'])
    recommendations = corr_df[corr_df['count'] > 500].sort_values('correlation', ascending=False)
    return recommendations.iloc[1:11]

# Search section
st.subheader("🔍 Get Movie Recommendations")
selected_movie = st.selectbox("Select a Movie", movies_list)

# Button
if st.button("Get Recommendations"):
    st.subheader(f"Top 10 Movies Similar to '{selected_movie}'")
    results = recommend(selected_movie)

    movies = list(results.index)
    correlations = list(results['correlation'])
    counts = list(results['count'])

    for i in range(len(movies)):
        col1, col2 = st.columns([1, 4])
        with col1:
            poster = fetch_poster(movies[i])
            st.image(poster, width=120)
        with col2:
            st.markdown(f"### {i+1}. {fix_name(movies[i])}")
            score = round(correlations[i] * 10, 1)
            st.write(f"⭐ Match Score: **{score}/10**")
            st.write(f"🎬 Total Ratings: **{int(counts[i])}**")
        st.divider()