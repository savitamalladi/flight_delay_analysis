import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import plotly.express as px


# Load the dataset 
@st.cache_data
def load_data():
    flight_data = pd.read_csv("Flight Data.csv")
    flight_data['Scheduled Hour'] = pd.to_datetime(flight_data['Scheduled departure time'], format='%H:%M').dt.hour
    return flight_data


flight_data = load_data()


# Sidebar filter for airline selection
airlines = ["All"] + flight_data['Carrier Code'].unique().tolist()
selected_airline = st.sidebar.selectbox("Filter by Airline", airlines)

# Filter data based on the selected airline
if selected_airline != "All":
    flight_data = flight_data[flight_data['Carrier Code'] == selected_airline]

# Visualizations Page
st.title("Flight Delay Analysis")
st.write("This page provides interactive visualizations to explore delay patterns over time and identify the causes of delays.")

# Tabs for different types of visualizations
tab1, tab2 = st.tabs(["Time", "Cause"])

### Tab 1: General Delay Analysis ###
with tab1:
    st.subheader("Delay Time Analysis")
    
    if selected_airline == "All":
        st.write("Analysis of delay in time and month for **all** airlines.")
    else:
        st.write(f"Analysis of delay in time and month for **{selected_airline}** airline.")

    st.markdown('---')


    # Visualization 1: Number of Delays per Month

    st.subheader("Number of Delays per Month")
    flight_data['Date (MM/DD/YYYY)'] = pd.to_datetime(flight_data['Date (MM/DD/YYYY)'], format='%m/%d/%Y')
    # Extract month and year for grouping
    flight_data['Month'] = flight_data['Date (MM/DD/YYYY)'].dt.strftime('%Y-%m')

    # Group by month and count the number of delays
    delays_per_month = (
        flight_data[flight_data['Departure delay (Minutes)'] > 15]
        .groupby('Month')
        .size()
        .reset_index(name='Number of Delays')
    )

    # months are ordered chronologically
    delays_per_month['Month'] = pd.to_datetime(delays_per_month['Month'], format='%Y-%m')
    delays_per_month = delays_per_month.sort_values('Month')

    # Ploting the bar chart
    fig = px.bar(
        delays_per_month,
        x='Month',
        y='Number of Delays',
        labels={'Month': 'Month', 'Number of Delays': 'Delays'}
    )

    st.plotly_chart(fig)
    if selected_airline == "All":
            st.write("This :blue[Bar Chart] illustrates the number of delayed flights per month across **all** airlines. It provides insights into the months with the highest delays, helping users make informed travel plans. Additionally, it allows for comparison with potential causes of delays to identify patterns.")
    else:
            st.write(f"This :blue[Bar Chart] illustrates the number of delayed flights per month in **{selected_airline}** airlines. It provides insights into the months with the highest delays, helping users make informed travel plans. Additionally, it allows for comparison with potential causes of delays to identify patterns.")

    st.markdown('---')


    # Visualization 2: Average Delay by Hour of Day
    st.subheader("Average Delay by Hour of Day")
    flight_data['Scheduled Hour'] = pd.to_datetime(flight_data['Scheduled departure time']).dt.hour
    hourly_avg_delay = flight_data.groupby('Scheduled Hour')['Departure delay (Minutes)'].mean().reset_index()
    hourly_avg_delay.columns = ['Scheduled Hour', 'Average Delay (Minutes)']
    fig2 = px.line(hourly_avg_delay, x="Scheduled Hour", y="Average Delay (Minutes)", color_discrete_sequence=["red"])
    st.plotly_chart(fig2)
    if selected_airline == "All":
            st.write("This :red[Line Chart] displays the average delay by each hour of the day across **all** airlines. It helps identify the hours with the longest delays, enabling users to better plan their flight schedules and avoid peak delay times.")
    else:
            st.write(f"This :red[Line Chart] displays the average delay by each hour of the day in **{selected_airline}** airlines. It helps identify the hours with the longest delays, enabling users to better plan their flight schedules and avoid peak delay times.")

    st.markdown('---')

    # Visualization 3: Heatmap of Delayed Flights by Month and Hour
    
    st.subheader("Heatmap of Delayed Flights by Month and Hour")

    # Convert Date and Scheduled Departure Time into useful formats
    flight_data['Date (MM/DD/YYYY)'] = pd.to_datetime(flight_data['Date (MM/DD/YYYY)'], format='%d/%m/%Y', errors='coerce')
    flight_data['Month'] = flight_data['Date (MM/DD/YYYY)'].dt.month_name()
    flight_data['Scheduled Hour'] = pd.to_datetime(flight_data['Scheduled departure time'], format='%H:%M', errors='coerce').dt.hour

    # Determine if a flight is delayed
    flight_data['IsDelayed'] = flight_data['Departure delay (Minutes)'] > 15

    # Grouping by Hour and Month for Delayed Flights
    delayed_flights = flight_data[flight_data['IsDelayed']].groupby(['Scheduled Hour', 'Month']).size().reset_index(name='Delayed Flights')

    # Order months for proper visualization
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    delayed_flights['Month'] = pd.Categorical(
        delayed_flights['Month'], 
        categories=month_order, 
        ordered=True
    )

    # Sort data for visualization
    delayed_flights = delayed_flights.sort_values(by=['Month', 'Scheduled Hour'])

    # Create the heatmap using Plotly
    fig = px.density_heatmap(
        delayed_flights,
        x='Month',
        y='Scheduled Hour',
        z='Delayed Flights',
        color_continuous_scale='Viridis',
        labels={
            'Scheduled Hour': 'Hour of Day',
            'Month': 'Month',
            'Delayed Flights': 'Number of Delayed Flights'
        },
    )

    # Ensure y-axis shows all hours (0-23)
    fig.update_yaxes(dtick=1, title_text="Hour of Day")

    # Display the heatmap
    st.plotly_chart(fig)

    # Add description
    if selected_airline == "All":
        st.write(
            "This :green[Heatmap] illustrates the number of delayed flights by hour and month across **all airlines**. "
            "It provides insights into when delays are most frequent, helping users analyze patterns and plan better."
        )
    else:
        st.write(
            f"This :green[Heatmap] illustrates the number of delayed flights by hour and month in **{selected_airline}** airlines. "
            "It helps users understand delay patterns specific to this airline for better decision-making."
        )

    st.markdown('---')
    



### Tab 2: Cause of Delays ###
with tab2:
    st.subheader("Delay Cause Analysis")
    if selected_airline == "All":
        st.write("Analysis of the cause of delay for **all** airlines.")
    else:
        st.write(f"Analysis of the cause of delay for **{selected_airline}** airline.")

    st.markdown('---')

    

    # Visualization 1: Delays by Weather Conditions
    st.subheader("Impact of Weather Conditions on Delays")
    weather_delays = flight_data.groupby('Weather Conditions')['Departure delay (Minutes)'].mean().reset_index()
    weather_delays.columns = ['Weather Conditions', 'Average Delay (Minutes)']
    fig4 = px.bar(weather_delays, x="Weather Conditions", y="Average Delay (Minutes)", color="Weather Conditions")
    st.plotly_chart(fig4)
    if selected_airline == "All":
        st.write("This :blue[Bar Chart] illustrates the impact of different weather conditions on flight delays across **all** airlines, showing the average delay time in minutes. It provides insights into how weather factors contribute to delays, helping users plan their travel during adverse weather conditions.")
    else:
        st.write(f"This :blue[Bar Chart] illustrates the impact of different weather conditions on flight delays in **{selected_airline}** airlines, showing the average delay time in minutes. It provides insights into how weather factors contribute to delays, helping users plan their travel during adverse weather conditions.")

    st.markdown('---')    


    # Visualization 2: Delays by Airport
    st.subheader("Average Delays by Origin Airport")
    airport_delays = flight_data.groupby('Origin Airport')['Departure delay (Minutes)'].mean().reset_index()
    airport_delays.columns = ['Origin Airport', 'Average Delay (Minutes)']
    fig5 = px.bar(airport_delays, x="Origin Airport", y="Average Delay (Minutes)", color="Origin Airport")
    st.plotly_chart(fig5)
    if selected_airline == "All":
        st.write("This :orange[Bar Chart] displays the average delay times in minutes for flights departing from various origin airports across **all** airlines. It helps identify airports with higher average delays, enabling users to plan their travel more effectively and understand potential bottlenecks in departure timings.")
    else:
        st.write(f"This :orange[Bar Chart] displays the average delay times in minutes for flights departing from various origin airports for **{selected_airline}** airlines. It helps identify airports with higher average delays, enabling users to plan their travel more effectively and understand potential bottlenecks in departure timings.")

    st.markdown('---')

    # Visualization 3: Delays by Airline
    st.subheader("Delays by Airline")
    airline_delays = flight_data.groupby('Carrier Code')['Departure delay (Minutes)'].mean().reset_index()
    airline_delays.columns = ['Carrier Code', 'Average Delay (Minutes)']
    fig6 = px.bar(airline_delays, x="Carrier Code", y="Average Delay (Minutes)", color="Carrier Code")
    st.plotly_chart(fig6)
    if selected_airline == "All":
        st.write("This :green[Bar Chart] displays the average delay times in minutes across **all** airlines. It provides insights into which airlines experience higher delays on average, helping users make informed decisions about their travel plans.")
    else:
        st.write(f"This :green[Bar Chart] displays the average delay times in minutes for **{selected_airline}** airlines.")

    st.markdown('---')

    # Avg delay by cause of delay
    st.subheader("Cause of Delay")
    
    delay_columns = [
        "Delay Carrier (Minutes)",
        "Delay Weather (Minutes)",
        "Delay National Aviation System (Minutes)",
        "Delay Security (Minutes)",
        "Delay Late Aircraft Arrival (Minutes)"
    ]

    # total delay per cause
    total_delays_per_cause = flight_data[delay_columns].sum()

    total_delay = total_delays_per_cause.sum()

    # percentage
    percentage_delays = (total_delays_per_cause / total_delay) * 100

    # data for the chart
    delay_data = pd.DataFrame({
        "Cause of Delay": total_delays_per_cause.index.str.replace("Delay ", "").str.replace(" (Minutes)", ""),
        "Percentage of Total Delay": percentage_delays
    })


    fig = px.bar(
        delay_data,
        x="Cause of Delay",
        y="Percentage of Total Delay",
        color="Cause of Delay",
        labels={"Percentage of Total Delay": "Percentage (%)", "Cause of Delay": "Cause of Delay"},
        text_auto=".2f"
    )

    st.plotly_chart(fig, use_container_width=True)
    if selected_airline == "All":
        st.write("This :red[Bar Chart] displays the percentage of flight delays caused by various factors across **all** airlines. It highlights the most common contributors to delays, helping airlines identify areas for improvement and enabling travelers to understand the primary causes of disruptions")
    else:
        st.write(f"This :red[Bar Chart] displays the percentage of flight delays caused by various factors for **{selected_airline}** airlines. It highlights the most common contributors to delays, helping airlines identify areas for improvement and enabling travelers to understand the primary causes of disruptions.")

    st.markdown('---')