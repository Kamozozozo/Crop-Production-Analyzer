import folium.map
import streamlit as st
import numpy as np
import pandas as pd
from pymongo import MongoClient
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import folium

# Connecting to the database
try:
    client = MongoClient('mongodb://localhost:27017')
    db = client['myDatabase']
    collection = db['myCollection']
except Exception as e:
    print("Error connecting to MongoDB:", e)

# Data retrieval function
def retrieve_data(country):
    data = collection.find({"Area": country})
    return list(data)

# Data processing
def process_data(data):
    try:
        df = pd.DataFrame(data)
        df = df.rename(columns={"hg/ha_yield":"yield","avg_temp": "Average Temperature", "average_rain_fall_mm_per_year": "Average Rainfall"})
        return df
    except:
        st.error("Data not available")

# Line plot function
def plot_line(df):
    try:
        fig, ax = plt.subplots()
        palette = list(sns.palettes.mpl_palette('Dark2'))
        for i, (series_name, series) in enumerate(df.groupby('Item')):
            xs = series['Year']
            ys = series['yield']
            ax.plot(xs, ys, label=series_name, color=palette[i % len(palette)])
        ax.legend(title='Item', bbox_to_anchor=(1, 1), loc='upper left')
        ax.set_title("Crop yields over the years")
        sns.despine()
        plt.xlabel('Years')
        plt.ylabel('Yield')
        st.pyplot(fig)
    except:
        st.error("Data not available")
#table for bar 
def table_bar(df):
    unique_items = df['Item'].unique()
    result_data = {'Item': [], 'propability': []}
    
    for item in unique_items:
        item_df = df[df['Item'] == item]
        X = item_df[['Year']]
        Y = item_df['yield']
        regression = LinearRegression()
        regression.fit(X, Y)
        score = regression.score(X, Y) 
        result_data['Item'].append(item)
        result_data['propability'].append('{:.1%}'.format(score))
        
    result_df = pd.DataFrame(result_data)
    st.dataframe(result_df)  # Display the resulting DataFrame

    
# Create dynamic pie chart
def create_dynamic_pie_chart(labels, sizes):
    fig, ax = plt.subplots(figsize=(10, 7))
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.set_title('Crops yield')
    ax.axis('equal')  
    def hover(event):
        for wedge, label in zip(wedges, labels):
            if wedge.contains(event)[0]:
                index = labels.tolist().index(label)
                ax.annotate(f"{label}: {sizes[index]:.2f}%", 
                            xy=(0, 0), 
                            xytext=(0.5, 0.5),
                            textcoords='axes fraction',
                            bbox=dict(boxstyle="round", fc="w", ec="gray", alpha=0.9),
                            arrowprops=dict(arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90,rad=10"))
    fig.canvas.mpl_connect('motion_notify_event', hover)
    st.pyplot(fig)

# Pie chart function
def Pie_chart(df):
    try:
        labels = df['Item'].unique()
        sizes = df.groupby('Item')['yield'].sum().values
        create_dynamic_pie_chart(labels, sizes)
    except:
        st.error("Data not available")

# Thematic map function
import streamlit as st
import plotly.graph_objects as go

def create_thematic_map(df):
    # Sample data (you can replace this with your own data)
    countries = [
    "Algeria", "Angola","Albania", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Central African Republic",
    "Egypt", "Eritrea", "Ghana", "Guinea", "Kenya", "Lesotho", "Libya", "Madagascar", "Malawi", "Mali",
    "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", "Rwanda", "Senegal", "South Africa",
    "Sudan", "Tunisia", "Uganda", "Zambia", "Zimbabwe"
    ]
    temperature_values = [17.65, 24.55, 10.36, 18.69, 29.41,11.26, 9.19, 25.69, 21.30, 23.12, 20.11, 19.43, 17.67, 26.11, 15.33, 16.45, 17.10, 18.30, 19.11, 20.90, 
                      21.0, 22.00, 23.30, 24.40, 25.10, 26.40, 27.40, 28.20, 29.20, 19.10, 19.80, 20.67, 16.0, 17.30, 19.30, 19.30, 15.40, 29.10, 
                      19.10, 22.20, 10.33, 20.90, 14.80, 14.40, 14.50, 14.60, 24.70, 24.80, 24.90, 25.22, 15.10, 15.20, 15.30, 15.40, 15.50]
    rainfall_values = [1890, 1010, 3522, 4541, 5512, 2165, 5475, 8545, 9225, 6105, 1165, 1259, 1035, 1405, 1555, 1655, 1475, 1485, 1965, 2205, 
                   2175, 2205, 2395, 2485, 2355, 1265, 1275, 2185, 2095, 1115, 9005, 3022, 935, 3454, 3505, 365, 3275, 1385, 
                   3905, 4005, 4185, 4205, 4135, 4245, 4515, 4645, 4755, 4285, 4915, 5035, 5145, 5425, 5356, 5645, 5585]

    # Create initial trace for temperature
    trace_temperature = go.Choropleth(
        locations=countries,  
        z=temperature_values,  
        locationmode='country names',
        colorscale='Reds',  # Red color scale
        colorbar_title='Average Temperature (°C)',  # Adjust the title according to your data
        marker_line_color='white',  # Add white borders between countries
        marker_line_width=0.5,  # Set the width of the borders
        visible=True
    )

    # Create trace for rainfall
    trace_rainfall = go.Choropleth(
        locations=countries,  
        z=rainfall_values,  
        locationmode='country names',
        colorscale='Blues',  # Blue color scale
        colorbar_title='Average Rainfall (mm)',  # Adjust the title according to your data
        marker_line_color='white',  # Add white borders between countries
        marker_line_width=0.5,  # Set the width of the borders
        visible=False
    )

    # Create figure with both traces
    fig = go.Figure(data=[trace_temperature, trace_rainfall])

    # Set layout options
    fig.update_layout(
        title='African Thematic Map',
        geo=dict(
            scope='africa',  # Set map scope to Africa
            showframe=True,  # Show the frame around the map
            showcoastlines=True,  # Show country coastlines
            coastlinecolor='black',  # Set the color of the coastlines
            showland=True,  # Show land area
            landcolor='rgb(245,245,245)',  # Set the color of land area
            projection_type='mercator'  # Set projection type to 'mercator'
        )
    )

    # Add dropdown menu for switching between temperature and rainfall
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=list([
                    dict(
                        args=[{'visible': [True, False]}],
                        label="Temperature",
                        method="update"
                    ),
                    dict(
                        args=[{'visible': [False, True]}],
                        label="Rainfall",
                        method="update"
                    )
                ]),
                direction="down",
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.1,
                yanchor="top"
            ),
        ]
    )
    return fig

# Use Streamlit to display the Plotly figure

# Main function
def main():
    st.markdown("<h1 style='text-align:center'> Please Choose a country<h1/>", unsafe_allow_html=True)
    african_countries = [
    "Algeria", "Angola","Albania", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Central African Republic",
    "Egypt", "Eritrea", "Ghana", "Guinea", "Kenya", "Lesotho", "Libya", "Madagascar", "Malawi", "Mali",
    "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", "Rwanda", "Senegal", "South Africa",
    "Sudan", "Tunisia", "Uganda", "Zambia", "Zimbabwe"
    ]

    with st.form("form"):
        selected_country = st.selectbox("Country", african_countries, key="selected_country")
        submit_button = st.form_submit_button("Search")

    if submit_button:
        # Retrieve and process data
        data = retrieve_data(selected_country)
        df = process_data(data)
        #st.dataframe(df)

        # Plot line graph
        st.write("Line Plot:")
        plot_line(df)
        table_bar(df)
        
        # Plot pie chart
        st.write("Pie Chart:")
        Pie_chart(df)

        # Thematic map
        st.write("Thematic Map:")
        st.plotly_chart(create_thematic_map(df))

# Run the main function
if __name__ == "__main__":
    main()
