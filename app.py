import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import numpy as np

# Set page config
st.set_page_config(page_title="Movie Ratings Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Movie class
class movies:
    def __init__(self, title, director, year, genre, rating):
        self.title = title
        self.director = director
        self.year = year
        self.genre = genre
        self.rating = rating

    def to_dict(self):
        return {
            "Title": self.title,
            "Director": self.director,
            "Year": self.year,
            "Genre": self.genre,
            "Rating": self.rating
        }

# Generate movie data (cached for performance)
@st.cache_data
def generate_movie_data():
    directors = {
        "Christopher Nolan": ["Sci-Fi", "Action", "Drama"],
        "Quentin Tarantino": ["Crime", "Drama"],
        "Martin Scorsese": ["Crime", "Drama"],
        "Steven Spielberg": ["Drama", "Adventure"],
        "Francis Ford Coppola": ["Crime", "Drama"],
        "James Cameron": ["Sci-Fi", "Action"],
        "Ridley Scott": ["Sci-Fi", "Drama"],
        "Denis Villeneuve": ["Sci-Fi", "Drama"],
        "Greta Gerwig": ["Drama"],
        "Jordan Peele": ["Horror", "Thriller"]
    }

    years = list(range(1970, 2025))

    director_rating_bias = {
        "Christopher Nolan": (8.0, 9.4),
        "Quentin Tarantino": (7.8, 9.2),
        "Martin Scorsese": (7.5, 9.3),
        "Steven Spielberg": (7.4, 9.0),
        "Francis Ford Coppola": (8.0, 9.5),
        "James Cameron": (7.2, 8.9),
        "Ridley Scott": (7.0, 8.8),
        "Denis Villeneuve": (7.6, 9.1),
        "Greta Gerwig": (7.0, 8.6),
        "Jordan Peele": (6.8, 8.5)
    }

    movie_list = []

    for i in range(1, 101):
        director = random.choice(list(directors.keys()))
        genre = random.choice(directors[director])
        year = random.choice(years)

        rating_min, rating_max = director_rating_bias[director]
        rating = round(random.uniform(rating_min, rating_max), 1)

        title = f"Movie {i}"

        movie_list.append(
            movies(title, director, year, genre, rating)
        )

    df = pd.DataFrame([movie.to_dict() for movie in movie_list])
    return df

# Load data
df = generate_movie_data()

# Title
st.title("🎬 Movie Ratings Dashboard")
st.markdown("---")

# Sidebar Filters
st.sidebar.header("🎯 Filters")

# Director filter
directors = df["Director"].unique().tolist()
selected_directors = st.sidebar.multiselect("Select Director(s):", directors, default=directors)

# Genre filter
genres = df["Genre"].unique().tolist()
selected_genres = st.sidebar.multiselect("Select Genre(s):", genres, default=genres)

# Year range filter
year_range = st.sidebar.slider("Year Range:", int(df["Year"].min()), int(df["Year"].max()), 
                                (int(df["Year"].min()), int(df["Year"].max())))

# Rating range filter
rating_range = st.sidebar.slider("Rating Range:", float(df["Rating"].min()), float(df["Rating"].max()), 
                                  (float(df["Rating"].min()), float(df["Rating"].max())), step=0.1)

# Apply filters
filtered_df = df[
    (df["Director"].isin(selected_directors)) &
    (df["Genre"].isin(selected_genres)) &
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1]) &
    (df["Rating"] >= rating_range[0]) &
    (df["Rating"] <= rating_range[1])
]

# Key Metrics
st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Movies", len(filtered_df))

with col2:
    avg_rating = filtered_df["Rating"].mean()
    st.metric("Average Rating", f"{avg_rating:.2f}")

with col3:
    highest_rating = filtered_df["Rating"].max()
    st.metric("Highest Rating", f"{highest_rating:.1f}")

with col4:
    lowest_rating = filtered_df["Rating"].min()
    st.metric("Lowest Rating", f"{lowest_rating:.1f}")

st.markdown("---")

# Main content area
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Overview", "👥 By Director", "🎭 By Genre", "📅 By Year", "🎥 Movie List"])

# Tab 1: Overview
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Rating Distribution
        fig_dist = px.histogram(filtered_df, x="Rating", nbins=20, 
                                title="Rating Distribution",
                                labels={"Rating": "Rating", "count": "Count"},
                                color_discrete_sequence=["#1f77b4"])
        fig_dist.update_layout(height=400)
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        # Rating by Year
        fig_year = px.scatter(filtered_df, x="Year", y="Rating", 
                              title="Ratings Over Time",
                              color="Rating",
                              color_continuous_scale="Viridis",
                              size="Rating")
        fig_year.update_layout(height=400)
        st.plotly_chart(fig_year, use_container_width=True)

# Tab 2: By Director
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Average Rating by Director
        director_avg = filtered_df.groupby("Director")["Rating"].agg(["mean", "count"]).reset_index()
        director_avg = director_avg.sort_values("mean", ascending=False)
        
        fig_director = px.bar(director_avg, x="Director", y="mean",
                              title="Average Rating by Director",
                              labels={"mean": "Average Rating"},
                              color="mean",
                              color_continuous_scale="RdYlGn")
        fig_director.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_director, use_container_width=True)
    
    with col2:
        # Movie Count by Director
        fig_count = px.bar(director_avg, x="Director", y="count",
                           title="Movie Count by Director",
                           labels={"count": "Count"},
                           color="count",
                           color_continuous_scale="Blues")
        fig_count.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_count, use_container_width=True)

# Tab 3: By Genre
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        # Average Rating by Genre
        genre_avg = filtered_df.groupby("Genre")["Rating"].agg(["mean", "count"]).reset_index()
        genre_avg = genre_avg.sort_values("mean", ascending=False)
        
        fig_genre = px.bar(genre_avg, x="Genre", y="mean",
                           title="Average Rating by Genre",
                           labels={"mean": "Average Rating"},
                           color="mean",
                           color_continuous_scale="RdYlGn")
        fig_genre.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_genre, use_container_width=True)
    
    with col2:
        # Genre distribution pie chart
        fig_pie = px.pie(filtered_df, names="Genre", title="Genre Distribution",
                         color_discrete_sequence=px.colors.qualitative.Set3)
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

# Tab 4: By Year
with tab4:
    # Box plot of ratings by year (grouped)
    year_grouped = filtered_df.copy()
    year_grouped["Year_Group"] = pd.cut(year_grouped["Year"], bins=6)
    
    fig_year_box = px.box(filtered_df, x="Year", y="Rating",
                          title="Rating Distribution by Year",
                          color_discrete_sequence=["#636EFA"])
    fig_year_box.update_layout(height=500)
    st.plotly_chart(fig_year_box, use_container_width=True)
    
    # Line chart of average rating over time
    yearly_avg = filtered_df.groupby("Year")["Rating"].mean().reset_index()
    
    fig_line = px.line(yearly_avg, x="Year", y="Rating",
                       title="Average Rating Trend Over Time",
                       markers=True,
                       color_discrete_sequence=["#EF553B"])
    fig_line.update_layout(height=400)
    st.plotly_chart(fig_line, use_container_width=True)

# Tab 5: Movie List
with tab5:
    st.subheader("Movie Database")
    
    # Sorting options
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox("Sort by:", ["Rating", "Year", "Title", "Director"])
    with col2:
        sort_order = st.selectbox("Order:", ["Descending", "Ascending"])
    
    # Apply sorting
    ascending = sort_order == "Ascending"
    sorted_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
    
    # Display data table
    st.dataframe(sorted_df, use_container_width=True)
    
    # Download CSV
    csv = sorted_df.to_csv(index=False)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="movies_data.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("*Dashboard created with Streamlit | Data contains 100 movies from various directors and genres*")
