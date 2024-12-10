import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.title("Flight Delay Analysis")

st.write("This web application provides visualizations of delay patterns by hour, month, and airline to help users understand flight delay trends.")
st.write("Here's to **:orange[Happy]** and **:green[Safe]** flying ✈️")

st.markdown('---')

st.header("🔧 How the Application is Built")
st.write("""
         This app is built with:
    - **Streamlit** for the interactive UI.
    - **Plotly** for interactive and visually appealing charts.
""")
st.markdown('---')

st.header("📝 Key Features")
st.write("""
1. :blue[Visualize] patterns in flight delays using charts and graphs.
2. :blue[Filter] flights and analyze delay trends interactively.
""")

st.markdown('---')

st.header("🧐 Purpose of the Project")
st.write("The purpose of this project is to provide insights into flight delays through data visualizations. By analyzing various factors such as carrier performance, weather conditions, and departure schedules, users can better understand the causes and patterns of delays. Additionally, this project can also help to assist airlines in optimizing their operations and help passengers make informed travel decisions. ")

st.markdown('---')