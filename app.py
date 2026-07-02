import streamlit as st
import pickle
import requests
import random
API_KEY = st.secrets["OMDB_API_KEY"]
def fetch_movie_details(title):
    url = f"https://www.omdbapi.com/?t={title}&apikey={API_KEY}"

    response = requests.get(url)
    data = response.json()

    if data.get("Response") == "True":
        return {
            "poster": data.get("Poster"),
            "rating": data.get("imdbRating"),
            "year": data.get("Year"),
            "runtime": data.get("Runtime"),
            "plot": data.get("Plot"),
            "language": data.get("Language")
        }

    return {
        "poster": None,
        "rating": "N/A",
        "year": "N/A",
        "runtime": "N/A",
        "plot": "No description available.",
        "language": "N/A"
    }

# Page Configuration
st.markdown("""
<style>

.stApp{
    background:#0E1117;
}

.main{
    padding-top:1rem;
}

h1{
    color:#FF4B4B;
    text-align:center;
}

h2,h3,h4{
    color:white;
}

div[data-testid="stMetric"]{
    background:#1C1F26;
    border-radius:15px;
    padding:18px;
    border:1px solid #333;
    text-align:center;
}

.stButton>button{
    width:100%;
    height:52px;
    border-radius:12px;
    background:#FF4B4B;
    color:white;
    font-weight:bold;
    font-size:18px;
    border:none;
}

.stButton>button:hover{
    background:#E63E3E;
}

div[data-testid="stSelectbox"]{
    margin-top:15px;
}

</style>
""", unsafe_allow_html=True)
# Load Files
movies = pickle.load(open("model/movie_list.pkl", "rb"))
similarity = pickle.load(open("model/similarity.pkl", "rb"))

# Recommendation Function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommended_movies = []

    for i in movie_list:

        movie_data = movies.iloc[i[0]]

        details = fetch_movie_details(movie_data.title)

        recommended_movies.append(
    {
        "title": movie_data.title,
        "similarity": round(float(i[1]) * 100, 2),

        "poster": details["poster"],
        "rating": details["rating"],
        "year": details["year"],
        "runtime": details["runtime"],
        "plot": details["plot"],
        "language": details["language"],

        "genres": movie_data["genres_display"],
        "director": movie_data["crew_display"][0],
        "cast": movie_data["cast_display"]
    }
)
    return recommended_movies



# UI
st.markdown("""
<h1>🎬 CineMatch AI</h1>

<h4 style="text-align:center;color:#bbbbbb;">
Find your next favorite movie using AI-powered recommendations.
</h4>
""", unsafe_allow_html=True)




col1, col2, col3 = st.columns(3)

col1.metric(
    "Movies",
    f"{len(movies):,}"
)

col2.metric(
    "Features",
    similarity.shape[1]
)

col3.metric(
    "Recommendations",
    5
)

col1, col2 = st.columns([4, 1])

with col1:
   # Search Movie
    selected_movie = st.selectbox(
        "🔍 Search a Movie",
        sorted(movies["title"].values)
    )

# Buttons
col1, col2 = st.columns(2)

with col1:
    recommend_btn = st.button(
        "🎯 Recommend",
        use_container_width=True
    )

with col2:
    surprise_btn = st.button(
        "🎲 Surprise Me",
        use_container_width=True
    )


if recommend_btn or surprise_btn:

    if surprise_btn:
        selected_movie = random.choice(movies["title"].tolist())
        st.success(f"🎲 Today's Pick: {selected_movie}")


    with st.spinner("Finding similar movies... 🍿"):

        recommendations = recommend(selected_movie)

        st.subheader("Recommended Movies")

        for i in range(0, len(recommendations), 3):

            cols = st.columns(3, gap="large")

            for col, movie in zip(cols, recommendations[i:i+3]):

                with col:

                   with st.container(border=True):

                        if movie["poster"] and movie["poster"] != "N/A":
                            st.image(movie["poster"], use_container_width=True)

                        st.markdown(f"### 🎬 {movie['title']}")

                        st.success(f"⭐ {movie['similarity']}% Match")

                        st.caption(f"⭐ IMDb: {movie['rating']}")

                        st.caption(f"📅 {movie['year']}")

                        st.caption(f"⏱️ {movie['runtime']}")

                        st.caption("🎭 " + " • ".join(movie["genres"][:3]))

                        st.caption(f"🎬 Director: {movie['director']}")

                        st.caption("👥 " + ", ".join(movie["cast"][:2]))

                        with st.expander("📝 Plot"):
                            st.write(movie["plot"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    with st.expander("📖 How does this recommendation system work?"):
        st.write("""
This is a **Content-Based Recommendation System**.

The model compares movies based on:
- Genres
- Overview
- Keywords
- Cast
- Director

These features are converted into vectors using **CountVectorizer**.

Recommendations are generated using **Cosine Similarity**.
""")
with st.sidebar:
    st.title("🎬 CineMatch AI")

    st.markdown("---")

    st.write("### About")

    st.write("""
This application recommends similar movies using a **Content-Based Recommendation System**.

### Technologies Used

- Python
- Pandas
- NumPy
- Scikit-Learn
- NLP
- Cosine Similarity
- Streamlit
""")

st.markdown("---")

st.markdown(
    """
<div style="text-align:center; color:gray; font-size:15px;">
🎬 <b>CineMatch AI</b><br><br>

Built with ❤️ using <b>Python • NLP • Scikit-Learn • Streamlit • OMDb API</b><br><br>

© 2026 <b>Surya</b>
</div>
""",
    unsafe_allow_html=True,
)