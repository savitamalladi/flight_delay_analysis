import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import plotly.express as px

# Sidebar for Navigation
page = st.sidebar.radio("Navigate", ["Home", "Prediction", "Visualizations"])

# Load Pretrained Model
@st.cache_resource
def load_model():
    with open("trained_model.pkl", "rb") as file:
        model = pickle.load(file)
    return model

# Load the dataset (for visualizations)
@st.cache_data
def load_data():
    flight_data = pd.read_csv("Flight Data.csv")
    flight_data['Scheduled Hour'] = pd.to_datetime(flight_data['Scheduled departure time'], format='%H:%M').dt.hour
    return flight_data

# Load Model and Data
model = load_model()
flight_data = load_data()

if page == "Home":
    st.title("✈️ Flight Delay Prediction App")
    st.markdown("""
    ### How It's Built
    This app is built with:
    - **Streamlit** for the interactive UI.
    - **Plotly** for interactive and visually appealing charts.
    - **Scikit-learn** for training the flight delay prediction model.
    
    ### Key Features
    1. Predict the probability of a flight being delayed based on:
        - Carrier Code
        - Origin and Destination Airports
        - Scheduled Hour of Departure
        - Weather Conditions
    2. Visualize patterns in flight delays using charts and graphs.
    3. Filter flights and analyze delay trends interactively.
    """)

# Page 1: Prediction
elif page == "Prediction":
    st.title("Flight Delay Prediction")

    # Input Columns
    col1, col2, col3 = st.columns(3)

    with col1:
        carrier = st.selectbox("Airline Carrier Code", flight_data['Carrier Code'].unique())
        origin = st.selectbox("Origin Airport", flight_data['Origin Airport'].unique())

    with col2:
        destination = st.selectbox("Destination Airport", flight_data['Destination Airport'].unique())
        travel_date = st.date_input("Date of Travel")

    with col3:
        scheduled_hour = st.slider("Scheduled Hour (0-23)", 0, 23, step=1)
        weather = st.selectbox("Weather Conditions", flight_data['Weather Conditions'].unique())

    # Prepare input for prediction
    input_data = pd.DataFrame({
        'Carrier Code': [carrier],
        'Origin Airport': [origin],
        'Destination Airport': [destination],
        'Weather Conditions': [weather],
        'Scheduled Hour': [scheduled_hour]
    })

    # One-hot encoding to match model input
    input_data = pd.get_dummies(input_data)
    input_data = input_data.reindex(columns=model.feature_names_in_, fill_value=0)

    # Predict
    if st.button("Predict"):
        prediction = model.predict(input_data)
        prediction_prob = model.predict_proba(input_data)[:, 1][0]  # Probability of delay

        # Display prediction and probability
        st.write(f"Prediction: {'Delayed' if prediction[0] == 1 else 'On Time'}")
        st.write(f"Probability of Delay: {prediction_prob * 100:.2f}%")

        # Show GIF based on probability range
        if prediction_prob < 0.3:
            st.image("on time.gif", caption="Congratulations, there is a low chance of delay!🥳 Your flight will mostly be on time.")
        elif 0.3 <= prediction_prob < 0.7:
            st.image("might be delayed.gif", caption="There might be a delay ugh😖 but also might not😌")
        else:
            st.image("delayed-flight-is-delayed.gif", caption="Sorry, your flight has a high chance of being delayed!😩")

# Page 2: Visualizations
elif page == "Visualizations":
    st.title("Dataset Visualizations")

    # Preprocessing for Visualizations
    flight_data['IsDelayed'] = (flight_data['Departure delay (Minutes)'] > 15).astype(int)

    

    avg_delay_by_carrier = flight_data.groupby('Carrier Code')['Departure delay (Minutes)'].mean().reset_index()
    fig = px.bar(avg_delay_by_carrier, 
                x='Carrier Code', 
                y='Departure delay (Minutes)', 
                title='Average Delay by Carrier',
                labels={'Departure delay (Minutes)': 'Avg Delay (Minutes)', 'Carrier Code': 'Carrier'})
    fig.update_layout(xaxis=dict(title="Carrier"), yaxis=dict(title="Average Delay (Minutes)"))
    st.plotly_chart(fig)


    avg_delay_by_hour = flight_data.groupby('Scheduled Hour')['Departure delay (Minutes)'].mean().reset_index()
    fig = px.line(avg_delay_by_hour, 
                x='Scheduled Hour', 
                y='Departure delay (Minutes)', 
                title='Average Delay by Hour of the Day',
                labels={'Scheduled Hour': 'Hour of the Day', 'Departure delay (Minutes)': 'Avg Delay (Minutes)'})
    fig.update_traces(mode='lines+markers')
    st.plotly_chart(fig)


    weather_delay = flight_data.groupby('Weather Conditions')['IsDelayed'].mean().reset_index()
    fig = px.pie(weather_delay, 
                names='Weather Conditions', 
                values='IsDelayed', 
                title='Delay Percentage by Weather Conditions',
                labels={'IsDelayed': 'Delay Probability'})
    st.plotly_chart(fig)




    # Preprocessing: Extract Hour and Month
    flight_data['Scheduled Hour'] = pd.to_datetime(flight_data['Scheduled departure time'], format='%H:%M').dt.hour
    flight_data['Month'] = pd.to_datetime(flight_data['Date (MM/DD/YYYY)']).dt.month_name()

    # Add Delay Flag
    flight_data['IsDelayed'] = flight_data['Departure delay (Minutes)'] > 20

    # Group by Hour and Month for Total Flights
    total_flights = flight_data.groupby(['Scheduled Hour', 'Month']).size().reset_index(name='Total Flights')

    # Group by Hour and Month for Delayed Flights
    delayed_flights = flight_data[flight_data['IsDelayed']].groupby(['Scheduled Hour', 'Month']).size().reset_index(name='Delayed Flights')

    # Merge Total and Delayed Flights
    heatmap_data = pd.merge(total_flights, delayed_flights, on=['Scheduled Hour', 'Month'], how='left')
    heatmap_data['Delayed Flights'] = heatmap_data['Delayed Flights'].fillna(0)

    # Calculate Delay Percentage
    heatmap_data['Delay Percentage'] = (heatmap_data['Delayed Flights'] / heatmap_data['Total Flights']) * 100

    # Fix Month Order
    month_order = [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]
    heatmap_data['Month'] = pd.Categorical(
        heatmap_data['Month'], 
        categories=month_order, 
        ordered=True
    )

    # Create Heatmap
    fig = px.density_heatmap(
        heatmap_data.sort_values("Month"),  # Sort by the custom month order
        x='Month',
        y='Scheduled Hour',
        z='Delay Percentage',
        color_continuous_scale='Viridis',
        labels={'Scheduled Hour': 'Hour of Day', 'Month': 'Month', 'Delay Percentage': 'Delay %'},
        title="Heatmap: Delay Percentage by Hour and Month"
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Hour of Day",
        coloraxis_colorbar=dict(title="Delay %"),
    )

    # Display Heatmap
    st.plotly_chart(fig)