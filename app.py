import streamlit as st
import pickle
import pandas as pd
import requests

# Load pickle files
user_movie_matrix_filled = pickle.load(open('user_movie_matrix_filled.pkl', 'rb'))
ratings_mean_count = pickle.load(open('ratings_mean_count.pkl', 'rb'))
movies_list = pickle.load(open('movies_list.pkl', 'rb'))

# TMDB API Key
API_KEY = "01fe5a4e8d21fd4e849dba6db1ab9965"

# Page config
st.set_page_config(page_title="Movie Recommender System", page_icon="🎬", layout="wide")

# Title
st.title("🎬 Movie Recommender System")
st.markdown("Select a movie and get top 10 similar movie recommendations!")

# Fetch poster function
def fetch_poster(movie_title):
    try:
        # Clean movie title (remove year)
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

# Recommend function
def recommend(movie_name):
    movie_ratings = user_movie_matrix_filled[movie_name]
    similar = user_movie_matrix_filled.corrwith(movie_ratings)
    corr_df = pd.DataFrame(similar, columns=['correlation'])
    corr_df.dropna(inplace=True)
    corr_df = corr_df.join(ratings_mean_count['count'])
    recommendations = corr_df[corr_df['count'] > 500].sort_values('correlation', ascending=False)
    return recommendations.iloc[1:11]

# Dropdown
selected_movie = st.selectbox("Select a Movie", movies_list)

# Button
if st.button("Get Recommendations"):
    st.subheader(f"Top 10 Movies Similar to '{selected_movie}'")
    results = recommend(selected_movie)

    # Display in rows of 5
    movies = list(results.index)
    correlations = list(results['correlation'])
    counts = list(results['count'])

    for i in range(0, len(movies), 5):
        cols = st.columns(5)
        for j, col in enumerate(cols):
            if i + j < len(movies):
                with col:
                    poster = fetch_poster(movies[i + j])
                    st.image(poster, use_column_width=True)
                    st.write(f"**{movies[i + j]}**")
                    st.caption(f"Correlation: {correlations[i+j]:.2f}")