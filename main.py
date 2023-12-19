import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import os

# Set page configuration
st.set_page_config(page_title="Boston Blue Bikes Data Explorer", layout="wide")

# Function to process data
def process_data(data, column='District', default_district='All'):
    filtered_data = data[data[column] == default_district] if default_district != 'All' else data
    average_docks = filtered_data["Total docks"].mean() if "Total docks" in filtered_data else 0
    return filtered_data, average_docks

# Load data from CSV and Excel
boston_data_csv = pd.read_csv('current_bluebikes_stations.csv', skiprows=[0], header=0, usecols=range(8))
boston_data_excel = pd.read_excel('boston_data.xlsx')

# Page Navigation
st.sidebar.title("Navigation")
selected_page = st.sidebar.radio("Choose a page", ["Home", "Map Visualization", "Charts", "Feedback"])

# Home Page
if selected_page == "Home":
    st.markdown("<h1 style='color: blue;'>Boston Blue Bikes Data Explorer</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: blue;'>Explore the usage patterns of Blue Bikes in Boston.</h3>", unsafe_allow_html=True)
    image_path = 'Bluebikes.png'
    st.image(image_path, use_column_width=True)

# Map Visualization Page
elif selected_page == "Map Visualization":
    st.subheader("Map of Bike Stations")
    column_index = 4
    show_all = st.sidebar.checkbox("Show all districts on map", value=True)

    if not show_all:
        districts = boston_data_csv.iloc[:, column_index].unique()
        district = st.sidebar.selectbox("Select a District", districts)
        filtered_data, avg_docks = process_data(boston_data_csv, column=boston_data_csv.columns[column_index], default_district=district)
    else:
        filtered_data, avg_docks = process_data(boston_data_csv)

    st.write(f"Average number of docks: {avg_docks:.2f}")
    tooltip = {
        "html": "<b>Station Name:</b> {Name}<br><b>District:</b> {District}<br><b>Deployment Year:</b> {Deployment Year}<br><b>Number of Docks:</b> {Total docks}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v11',
        initial_view_state=pdk.ViewState(latitude=42.3601, longitude=-71.0589, zoom=12, pitch=50),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=filtered_data,
                get_position='[Longitude, Latitude]',
                get_color='[200, 30, 0, 160]',
                get_radius=100,
                pickable=True
            )
        ],
        tooltip=tooltip
    ))

# Charts Page
elif selected_page == "Charts":
    st.header("Deployment Year Distribution")
    deployment_year_data = boston_data_excel['Deployment Year'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(deployment_year_data, labels=deployment_year_data.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

    st.header("Number of Stations per District")
    station_count_all_districts = boston_data_csv.groupby("District")["Number"].nunique()
    st.bar_chart(station_count_all_districts)

    st.header("Average Docks per Station per District")
    avg_docks_per_district = boston_data_csv.groupby("District")["Total docks"].mean()
    st.line_chart(avg_docks_per_district)

# Feedback Page
elif selected_page == "Feedback":
    st.header("Feedback")
    feedback_text = st.text_area("Share your feedback or suggestions:")
    rating = st.slider("Rate (1 = Not Useful, 5 = Very Useful)", 1, 5)

    if st.button("Submit Feedback"):
        feedback_file = 'feedback.csv'
        if os.path.exists(feedback_file):
            feedback_data = pd.read_csv(feedback_file)
        else:
            feedback_data = pd.DataFrame(columns=['Feedback', 'Rating'])

        new_feedback = pd.DataFrame({'Feedback': [feedback_text], 'Rating': [rating]})
        feedback_data = pd.concat([feedback_data, new_feedback], ignore_index=True)
        feedback_data.to_csv(feedback_file, index=False)
        st.success("Thank you for your feedback!")
