'''
Adrian Pena
CS 230 - Section 7 Async
Global Power Plants Dataset
LLM Tool: Gemini
URL: []
Description: Interactive explorer that analyzes
power plant capacity and fuel type in the UK,
India, Brazil, Germany, France, Canada
'''

import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt

# Add the web page title, icon, format
st.set_page_config(
    page_title="Global Power Plants Tool",  # Title of the website when opened
    layout='wide',  # Print the text on the left of the screen
    page_icon='images/page_icon.jpg'  # Gives the site an icon, AI generated
)
# This gives my site a little more customization.
# I set the relative path for the icon image in the images folder

# [DICT_DRIVEN] IDENTIFY & EXPLAIN
# The dictionary below stores each of the different fuel types as keys.
# It includes nested dictionaries as values for each key, the keys for which
# are the color associated with the fuel and the category that it belongs in
# Example: FUEL_TYPES['Coal']['Category'] = 'Fossil'
FUEL_TYPES = {
    'Hydro': {'color': [0, 119, 182, 180], 'category': 'Renewable'},
    'Solar': {'color': [255, 183, 3, 180], 'category': 'Renewable'},
    'Wind': {'color': [144, 224, 239, 180], 'category': 'Renewable'},
    'Biomass': {'color': [42, 157, 143, 180], 'category': 'Renewable'},
    'Wave and Tidal': {'color': [72, 202, 228, 180], 'category': 'Renewable'},
    'Geothermal': {'color': [231, 111, 81, 180], 'category': 'Renewable'},
    'Coal': {'color': [50, 50, 50, 180], 'category': 'Fossil'},
    'Gas': {'color': [244, 162, 97, 180], 'category': 'Fossil'},
    'Oil': {'color': [108, 117, 125, 180], 'category': 'Fossil'},
    'Nuclear': {'color': [157, 78, 221, 180], 'category': 'Nuclear'},
    'Waste': {'color': [138, 129, 124, 180], 'category': 'Other'},
    'Cogeneration': {'color': [203, 153, 126, 180], 'category': 'Other'},
    'Storage': {'color': [181, 131, 141, 180], 'category': 'Other'},
    'Other': {'color': [173, 181, 189, 180], 'category': 'Other'}
}
# Why I chose it: Having each of the fuel types color coded on my map will add
# to the visualization aspect of the map
# What I changed: Nothing, this is from the AI


# st.cache here allows streamlit can cache the values of the function below,
# which leads to faster loading times. 
@st.cache_data
def load_and_clean_data(data = 'power_plants_6_countries.csv'):  # Default argument for the data
    df = pd.read_csv(data)  # Read the data from the csv
    df = df.drop('gppd_idnr', axis=1)  # Removing this column because it is in the way and pointless

    # [STR_CLEAN] REVISE / REWRITE
    # My goal here was to clean the country name, plant name, and fuel type columns
    # AI initially wrote these lines using .astype(str), which I'm not as familiar with
    # I changed the code to only use .strip(), .split(), and .join() as well as list comp
    # Fuel and country name just used .strip(), plant name used .join() and .split()
    # because some of the names had extra spaces
    # Example: 'West  Burton CCGT ' --> 'West Burton CCGT'
    df['country_long'] = [row.strip() for row in df['country_long']]
    df['name'] = [' '.join(row.split()) for row in df['name']]  # Using .join and .split() instead
    df['primary_fuel'] = [row.strip() for row in df['primary_fuel']]

    # [REUSE_FUNC] REVISE / REWRITE
    # This custom function takes in the column name, minimum, and maximum allowed value
    # It validates the data to make sure there is nothing unexpected
    # I will run the latitudes, longitudes, and fuel capacities through this
    def validate_ints(column, min_bound, max_bound = float('inf')):  # max_bound has a default of infinity
        for row in df[column]:
            value = float(row)  # Turn the row into a float variable
            if value < min_bound or value > max_bound:  # Validate it
            # Stopping the program all together
                st.warning(f'There is invalid data in the {column} column')
                st.stop()

        return df[column]  # Return the validated column

    # I run the three relevant numeric columns through the custom function, validate_ints()
    df['capacity_mw'] = validate_ints('capacity_mw', 0)  # No third argument, it'll go to default
    df['latitude'] = validate_ints('latitude', -90, 90)
    df['longitude'] = validate_ints('longitude', -180, 180)


    # [LIST_OF_DICTS] REVISE / REWRITE
    # This section creates a new column in the dataframe that contains
    # the color code for each row. It goes through each key-value pair
    # of the main dictionary and makes a new dictionary with the fuel type
    # as the key and the color code as the value before adding it to the dataframe.
    # AI wrote this initially as a dictionary comprehension,
    # so I simplified to something I understood better
    color_map = {}
    category_map = {}
    for fuel_type, value in FUEL_TYPES.items(): # Go through each key-value pair in the main dictionary
        color_map[fuel_type] = value['color']
        category_map[fuel_type] = value['category']
    # Add a key value to color_map: fuel type as key and color code as value
    # Example: 'Hydro': 'color': [0, 119, 182, 180], 'category': 'Renewable'
    # Turns into: 'Hydro': [0, 119, 182, 180]
    df['color'] = df['primary_fuel'].map(color_map)
    df['category'] = df['primary_fuel'].map(category_map)

    return df  # End of the data cleaning function
    

df = load_and_clean_data()  # Run the function to clean the data

# Add the title, subheader, and sidebar header
st.title('Global Power Plants Tool')
st.subheader('U.K., Brazil, France, India, Germany, and Canada')
st.sidebar.header("Map Navigation & Filters")


# ----QUESTION 1 STARTS HERE----


# [LIST_COMP] IDENTIFY & EXPLAIN
# The list comprehension below creates a list containing the countries in the dataset
# It goes through each row of the country name column and adds that country to the list
# only if they aren't already in the list, because of the .unique(). It also sorts them.
# Example: ['UK', 'Germany', 'France', 'Germany'] --> ['France', 'Germany', 'UK']
# in regular form:
# for country in df['country_long'].unique():
#    countries.append(country)
# sorted(countries)
countries = sorted([country for country in df['country_long'].unique()])
# Germany is the default, only if Germany is in the dataset
default_idx = countries.index('Germany') if 'Germany' in countries else 0
# The user chooses a country with a select box in the sidebar
selected_country = st.sidebar.selectbox('Select Country', options=countries, index=default_idx)

country_df = df[df['country_long'] == selected_country]
# This creates a new dataframe that only contains
# the power plant data for the country that the user selected

max_cap = int(country_df['capacity_mw'].max())
# These lines create the slider on the sidebar. The max_cap is
# whatever the maximum plant capacity is in that country
min_cap = st.sidebar.slider(
    'Minimum Capacity (MW)',
    min_value=0,
    max_value=max_cap,  # Max on the slider is the one calculated earlier
    value=20,  # The slider is at 20 by default
    step=10  # The slider moves by 10
)

# Creating a list of the available fuel types that are present in the data for the selected country
# Without this, the user might be able to select a fuel type where there are no plants.
available_fuels = sorted(country_df['primary_fuel'].unique().tolist())
selected_fuels = st.sidebar.multiselect(
    'Select Fuel Types',
    options=available_fuels,  # The options is the list of availble fuels
    default=available_fuels[1:5]  # I put the default value as only a couple of types
)

# This section filters out the power plants in the data to only
# the ones that match the selected minimum capacity and fuel type
# Saved as its own dataframe
filtered_df = country_df[
    (country_df['capacity_mw'] >= min_cap)  # Making sure fuel cap is high enough
    & (country_df['primary_fuel'].isin(selected_fuels))  # Making sure fuel type is in the selection
    ]

st.subheader(f'Question 1: Active Power Plants in {selected_country} (≥ {min_cap} MW)')
# Print the header for this question

if filtered_df.empty:  # If there are no power plants matching the selected filters
    st.warning('No power plants match your filters.')  # Do not display the map, but rather a warning
else:  # If there are plants matching the filters
    view_state = pdk.ViewState(  # PyDeck function to define the initial view state
        latitude=filtered_df['latitude'].mean(),  # Latitude is set to the average of the matching data
        longitude=filtered_df['longitude'].mean(),  # Longitude is the same deal
        zoom=4.5,  # A zoom of 4.5 shows most of each country, but Canada
        pitch=0  # Ignoring pitch for this, makes 3D
    )
# This was the same PyDeck map format that we used in class, it works and is easy
# to understand. I tweaked the zoom a little bit to look better

# This section will define the 'layer' to use on the map
# Essentially which points to display and what they will look like
    layer = pdk.Layer(
        'ScatterplotLayer',
    # Only display the plants matching the filters
        data=filtered_df,
    # Their positions on the map are the lat and long column
        get_position=['longitude', 'latitude'],
    # Getting the color for the point based on the dictionary value from earlier
        get_color='color',  # This is why I added the color column earlier
    # The radius of each map point will increase with the plant's capacity
        get_radius='capacity_mw * 15 + 3000',
        pickable=True,  # Allows the plant name and capacity to display when I hover over it
        auto_highlight=True  # Highlights the plant when I hover over it
    )

# These lines are defining the tooltip dictionary to be used later with the PyDeck map
# <b> makes it bold, <br> is a line break
# {name} and the others are column placeholders, not f strings
    tooltip = {
        "html": "<b>Plant:</b> {name}<br/><b>Capacity:</b> {capacity_mw} MW<br/><b>Fuel:</b> {primary_fuel}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

# This is putting the previous sections together and making the map
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip
    ))

    st.caption(  # This is simply a caption at the bottom of the map
        f'Showing {len(filtered_df):,} power plant(s) totaling {filtered_df['capacity_mw'].sum():,.1f} MW.'
        )


# ----QUESTION 2 STARTS HERE----


st.divider()
st.subheader('Question 2: National Generating Capacity & Fuel Mix Comparison')

# This creates three columns so streamlit prints them side-by-side
col1, col2, col3 = st.columns(3)

with col1:  # The code in each 'with' statement will only affect the relevant column
    default_c1 = countries.index('Germany') if 'Germany' in countries else 0
    country1 = st.selectbox('Select First Country', options=countries, index=default_c1)
with col2:
    default_c2 = countries.index('France') if 'France' in countries else 0
    country2 = st.selectbox('Select Second Country', options=countries, index=default_c2)
with col3:
    metric = st.radio(
        'Comparison Metric',
        options=['Total Capacity (MW)', 'Percentage Share (%)'],
    )

if country1 == country2:
    st.warning('You selected the same country twice. Choose two different countries.')
else:
    comp_df = df[df['country_long'].isin([country1, country2])]
    grouped_df = comp_df.groupby(["primary_fuel", "country_long"])["capacity_mw"].sum()
    pivot_df = grouped_df.unstack(fill_value=0)
    pivot_df = pivot_df[[country1, country2]]

    if metric == 'Percentage Share (%)':
        pivot_df[country1] = (pivot_df[country1] / pivot_df[country1].sum()) * 100
        pivot_df[country2] = (pivot_df[country2] / pivot_df[country2].sum()) * 100
        y_label = 'Share of National Capacity (%)'
        chart_title = f'Fuel Mix Share: {country1} vs. {country2}'
    else:
        y_label = 'Installed Capacity (MW)'
        chart_title = f"Total Generating Capacity by Fuel: {country1} vs. {country2}"

    fig, ax = plt.subplots(figsize=(10, 5))
    pivot_df.plot(kind="bar", ax=ax, color=["#1f77b4", "#ff7f0e"], width=0.75, edgecolor="black")

    ax.set_title(chart_title, fontsize=15, fontweight="bold")
    ax.set_xlabel("Primary Fuel Type", fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.legend(title="Country")  # Creates the top right legend
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()  # Flattened the graph a little bit, more aesthetic

    st.pyplot(fig)


# ----QUESTION 3 STARTS HERE----


st.divider()
st.subheader("Question 3: Clean vs. Conventional Capacity & Top Power Plants")

q3_col1, q3_col2 = st.columns(2)

default_q3 = countries.index("Germany") if "Germany" in countries else 0
q3_country = q3_col1.selectbox("Select Country for Breakdown", options=countries, index=default_q3)
top_n = q3_col2.slider("Number of Top Plants to Display", min_value=5, max_value=20, value=10, step=1)

q3_df = df[df["country_long"] == q3_country]

cat_totals = q3_df.groupby("category")["capacity_mw"].sum()

# Color map for the four energy categories
CATEGORY_COLORS = {
    "Renewable": "#2a9d8f",
    "Fossil": "#495057",
    "Nuclear": "#9d4edd",
    "Other": "#adb5bd"
}
pie_colors = [CATEGORY_COLORS.get(cat, "#cccccc") for cat in cat_totals.index]

chart_col, table_col = st.columns([1.1, 1])

fig2, ax2 = plt.subplots(figsize=(6, 5))
wedges, texts, autotexts = ax2.pie(
    cat_totals.values,
    labels=cat_totals.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=pie_colors,
    pctdistance=0.78,
    wedgeprops={"width": 0.45, "edgecolor": "white", "linewidth": 2}
)

for text in autotexts:
    text.set_color("white")
    text.set_fontweight("bold")
    text.set_fontsize(10)

ax2.set_title(f"{q3_country} Capacity Share by Energy Category", fontsize=13, fontweight="bold")
ax2.legend(cat_totals.index, title="Category", loc="best")
plt.tight_layout()
chart_col.pyplot(fig2)

top_plants_df = q3_df.sort_values(by="capacity_mw", ascending=False).head(top_n)

top_plants_list = []
for _, row in top_plants_df.iterrows():
    plant_info = {
        "Plant Name": row["name"],
        "Primary Fuel": row["primary_fuel"],
        "Category": row["category"],
        "Capacity (MW)": round(row["capacity_mw"], 1)
    }
    top_plants_list.append(plant_info)

table_col.markdown(f"**Top {top_n} Largest Power Plants in {q3_country}**")
table_col.dataframe(top_plants_list, use_container_width=True, hide_index=True)

total_mw = q3_df["capacity_mw"].sum()
renewable_mw = cat_totals.get("Renewable", 0)
renewable_pct = (renewable_mw / total_mw) * 100 if total_mw > 0 else 0
st.caption(
    f"{q3_country} has {total_mw:,.1f} MW of total installed capacity, of which "
    f"{renewable_mw:,.1f} MW ({renewable_pct:.1f}%) comes from renewable sources."
)
