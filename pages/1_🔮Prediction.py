import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import plotly.express as px

# Loading Pretrained Model
@st.cache_resource
def load_model():
    with open("trained_model.pkl", "rb") as file:
        model = pickle.load(file)
    return model

# Load the dataset 
@st.cache_data
def load_data():
    flight_data = pd.read_csv("Flight Data.csv")
    flight_data['Scheduled Hour'] = pd.to_datetime(flight_data['Scheduled departure time'], format='%H:%M').dt.hour
    return flight_data

model = load_model()
flight_data = load_data()

st.title(':blue[Flight Delay Prediction]')

st.write("This feature predicts whether a flight will be delayed based on the inputs listed below. The app uses a machine learning model to provide a clear prediction — :green[**On Time**] or :red[**Delayed**] — along with the delay probability percentage, helping users plan their travel better.")
st.markdown('---')

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
        st.write(f"Prediction: {':red[Delayed]' if prediction[0] == 1 else ':blue[On Time]'}")
        st.write(f"Probability of Delay: {prediction_prob * 100:.2f}%")

        # Show GIF based on probability range
        if prediction_prob < 0.3:
            st.image("images/on time.gif", caption="Congratulations, there is a low chance of delay!🥳 Your flight will mostly be on time.")
        elif 0.3 <= prediction_prob < 0.7:
            st.image("images/might be delayed.gif", caption="There might be a delay ugh😖 but also might not😌")
        else:
            st.image("images/delayed-flight-is-delayed.gif", caption="Sorry, your flight has a high chance of being delayed!😩")

st.markdown('---')
