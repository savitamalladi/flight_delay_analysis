import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import plotly.express as px

st.title("Flight Delay Prediction & Statistics")

st.write("This web application predicts flight delays and provides visualizations of delay patterns by hour, month, and airline to help users understand flight delay trends.")
st.write("Here's to **:orange[Happy]** and **:green[Safe]** flying ✈️")

st.markdown('---')

st.header("🔧 How the Application is Built")
st.write("""
         This app is built with:
    - **Streamlit** for the interactive UI.
    - **Plotly** for interactive and visually appealing charts.
    - **Scikit-learn** for training the flight delay prediction model.""")

st.markdown('---')

st.header("📝 Key Features")
st.write("""
1. :blue[Predict] the probability of a flight being delayed based on:
   - **Carrier Code**
   - **Origin and Destination Airports**
   - **Scheduled Hour of Departure**
   - **Weather Conditions**
2. :blue[Visualize] patterns in flight delays using charts and graphs.
3. :blue[Filter] flights and analyze delay trends interactively.
""")

st.markdown('---')

st.header("🧐 Purpose of the Project")
st.write("The purpose of this project is to provide insights into flight delays through predictive modeling and data visualizations. By analyzing various factors such as carrier performance, weather conditions, and departure schedules, users can better understand the causes and patterns of delays. Additionally, this project can also help to assist airlines in optimizing their operations and help passengers make informed travel decisions. ")

st.markdown('---')