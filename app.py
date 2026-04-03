import streamlit as st
import pickle
import pandas as pd

# Load pickle files
user_movie_matrix_filled = pickle.load(open('user_movie_matrix_filled.pkl', 'rb'))
ratings_mean_count = pickle.load(open('ratings_mean_count.pkl', 'rb'))
movies_list = pickle.load(open('movies_list.pkl', 'rb'))

# Page config
st.set_page_config(page_title="Movie Recommender System", page_icon="🎬", layout="wide")

# Title
st.title("🎬 Movie Recommender System")
st.markdown("Select a movie and get top 10 similar movie recommendations!")

# Dropdown
selected_movie = st.selectbox("Select a Movie", movies_list)

# Recommend function
def recommend(movie_name):
    movie_ratings = user_movie_matrix_filled[movie_name]
    similar = user_movie_matrix_filled.corrwith(movie_ratings)
    corr_df = pd.DataFrame(similar, columns=['correlation'])
    corr_df.dropna(inplace=True)
    corr_df = corr_df.join(ratings_mean_count['count'])
    recommendations = corr_df[corr_df['count'] > 500].sort_values('correlation', ascending=False)
    return recommendations.iloc[1:11]

# Button
if st.button("Get Recommendations"):
    st.subheader(f"Top 10 Movies Similar to '{selected_movie}'")
    results = recommend(selected_movie)
    
    for i, (title, row) in enumerate(results.iterrows()):
        st.write(f"**{i+1}. {title}**")
        st.progress(float(row['correlation']))
        st.caption(f"Correlation: {row['correlation']:.2f} | Total Ratings: {int(row['count'])}")
        st.divider()