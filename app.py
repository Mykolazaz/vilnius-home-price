import streamlit as st
import pydeck as pdk
from geopy.geocoders import Nominatim

import pandas as pd
import geopandas as gpd

import pickle as pkl
import numpy as np

from scipy.spatial.distance import cdist


@st.cache_resource
def load_model():
    with open('model.pkl', 'rb') as f:
        model = pkl.load(f)
    return model

model = load_model()


st.title('Vilnius Apartment Nostradamus')
st.write('This is an open-source app that calculates apartment price based on data gathered from Aruodas.lt.')
st.write('Your input data is not collected.')

col1, col2 = st.columns(2)
with col1:
    area = st.number_input("Area, m²", max_value=350)
with col2:
    rooms = st.number_input("Number of rooms", step=1, max_value=12)

col3, col4 = st.columns(2)
with col3:
    floor = st.number_input("Floor", step=1, max_value=50)
with col4:
    floors = st.number_input("Total number of floors", step=1, max_value=50)

building_types = [
    {"display_name":"Mūrinis (Brick)", "input_name":"Mūrinis"},
    {"display_name":"Blokinis (Block)", "input_name":"Blokinis"},
    {"display_name":"Monolitinis (Monolithic)", "input_name":"Monolitinis"},
    {"display_name":"Medinis (Wooden)", "input_name":"Medinis"},
    {"display_name":"Rąstinis (Log)", "input_name":"Rąstinis"},
    {"display_name":"Karkasinis (Frame)", "input_name":"Karkasinis"},
    {"display_name":"Skydinis (Panel)", "input_name":"Skydinis"},
    {"display_name":"Kita (Other)", "input_name":"Kita"}
]

def format_display_name(record):
    return record["display_name"]

building_type = st.selectbox(
    "Select building type",
    options=building_types,
    format_func=format_display_name
)

building_type = building_type["input_name"]


heating_options = [
    {"display_name": "Centrinis kolektorinis (Central collector)", "input_name": "Centrinis kolektorinis"},
    {"display_name": "Centrinis (Central)", "input_name": "Centrinis"},
    {"display_name": "Dujinis (Gas)", "input_name": "Dujinis"},
    {"display_name": "Aeroterminis (Aerothermal)", "input_name": "Aeroterminis"},
    {"display_name": "Elektra (Electricity)", "input_name": "Elektra"},
    {"display_name": "Kietu kuru (Solid fuel)", "input_name": "Kietu kuru"},
    {"display_name": "Geoterminis (Geothermal)", "input_name": "Geoterminis"},
    {"display_name": "Elektra, aeroterminis (Electricity, aerothermal)", "input_name": "Elektra, aeroterminis"},
    {"display_name": "Centrinis, elektra (Central, electricity)", "input_name": "Centrinis, elektra"},
    {"display_name": "Centrinis, centrinis kolektorinis (Central, central collector)", "input_name": "Centrinis, centrinis kolektorinis"},
    {"display_name": "Centrinis kolektorinis, dujinis (Central collector, gas)", "input_name": "Centrinis kolektorinis, dujinis"},
    {"display_name": "Kita (Other)", "input_name": "Kita"}
]

heating = st.selectbox(
    "Select heating type",
    options=heating_options,
    format_func=format_display_name
)

heating = heating["input_name"]


furnishing_options = [
    {"display_name": "Įrengtas (Furnished)", "input_name": "Įrengtas"},
    {"display_name": "Dalinė apdaila (Partially furnished)", "input_name": "Dalinė apdaila"},
    {"display_name": "Neįrengtas (Unfurnished)", "input_name": "Neįrengtas"},
    {"display_name": "Nebaigtas statyti (Unfinished)", "input_name": "Nebaigtas statyti"},
    {"display_name": "Kita (Other)", "input_name": "Kita"}
]

furnishing = st.selectbox(
    "Select furnishing type",
    options=furnishing_options,
    format_func=format_display_name
)

furnishing = furnishing["input_name"]


feature_options = [
    {"display_name": "Uždaras kiemas (Enclosed courtyard)", "input_name": "enclosed_courtyard"},
    {"display_name": "Nauja elektros instaliacija (New electrical wiring)", "input_name": "new_electrical_wiring"},
    {"display_name": "Aukcionas (On auction)", "input_name": "on_auction"},
    {"display_name": "Tualetas ir vonia atskirai (Separate toilet & bathroom)", "input_name": "separate_toilet_bathroom"},
    {"display_name": "Renovuotas namas (Renovated building)", "input_name": "renovated"},
    {"display_name": "Virtuvė sujungta su kambariu (Kitchen connected to living room)", "input_name": "kitchen_connected_to_living_room"},
    {"display_name": "Aukštos lubos (High ceilings)", "input_name": "high_ceilings"},
    {"display_name": "Butas palėpėje (Attic apartment)", "input_name": "attic_apartment"},
    {"display_name": "Internetas (Internet)", "input_name": "internet"},
    {"display_name": "Liftas (Elevator)", "input_name": "elevator"},
    {"display_name": "Butas per kelis aukštus (Multi-level apartment)", "input_name": "multi_level_apartment"},
    {"display_name": "Kabelinė televizija (Cable TV)", "input_name": "cable_tv"},
    {"display_name": "Nauja kanalizacija (New sewerage system)", "input_name": "new_sewerage_system"},
    {"display_name": "Atskiras įėjimas (Separate entrance)", "input_name": "separate_entrance"},
    {"display_name": "Terasa (Terrace)", "input_name": "terrace"},
    {"display_name": "Palėpė (Attic)", "input_name": "attic"},
    {"display_name": "Drabužinė (Closet)", "input_name": "closet"},
    {"display_name": "Pirtis (Sauna)", "input_name": "sauna"},
    {"display_name": "Vieta automobiliui (Parking space)", "input_name": "parking_space"},
    {"display_name": "Rūsys (Basement)", "input_name": "basement"},
    {"display_name": "Balkonas (Balcony)", "input_name": "balcony"},
    {"display_name": "Sandėliukas (Storage room)", "input_name": "storage_room"},
    {"display_name": "Skalbimo mašina (Washing machine)", "input_name": "washing_machine"},
    {"display_name": "Šaldytuvas (Fridge)", "input_name": "fridge"},
    {"display_name": "Šildomos grindys (Heated floors)", "input_name": "heated_floors"},
    {"display_name": "Kondicionierius (Air conditioner)", "input_name": "air_conditioner"},
    {"display_name": "Su baldais (With furniture)", "input_name": "with_furniture"},
    {"display_name": "Viryklė (Stove)", "input_name": "stove"},
    {"display_name": "Indaplovė (Dishwasher)", "input_name": "dishwasher"},
    {"display_name": "Židinys (Fireplace)", "input_name": "fireplace"},
    {"display_name": "Vonia (Bathtub)", "input_name": "bathtub"},
    {"display_name": "Rekuperacinė sistema (Recuperation system)", "input_name": "recuperation_system"},
    {"display_name": "Dušo kabina (Shower cabin)", "input_name": "shower_cabin"},
    {"display_name": "Virtuvės komplektas (Kitchen set)", "input_name": "kitchen_set"},
    {"display_name": "Plastikiniai vamzdžiai (Plastic pipes)", "input_name": "plastic_pipes"},
    {"display_name": "Signalizacija (Alarm system)", "input_name": "alarm_system"},
    {"display_name": "Budintis sargas (Security guard)", "input_name": "security_guard"},
    {"display_name": "Šarvuotos durys (Armored door)", "input_name": "armored_door"},
    {"display_name": "Kodinė laiptinės spyna (Code-locked stairway)", "input_name": "code_locked_stairway"},
    {"display_name": "Vaizdo kameros (Security cameras)", "input_name": "security_cameras"}
]

selected_options = st.multiselect(
    "Select all relevant features",
    options=feature_options,
    format_func=format_display_name
)

selected_features = [option["input_name"] for option in selected_options]

lat = None
lon = None

address_input = st.text_input("Enter address", placeholder='Naugarduko g. 24')
if address_input:
    geolocator = Nominatim(user_agent="streamlit_app")
    location = geolocator.geocode(address_input, timeout=10)
    if location:
        lat, lon = location.latitude, location.longitude
        st.write("Coordinates:", lat, lon)

        deck = pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=lat,
                longitude=lon,
                zoom=14,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=[{"lat": lat, "lon": lon}],
                    get_position=["lon", "lat"],
                    get_radius=25,
                    get_fill_color=[255, 0, 0, 160],
                    pickable=True,
                )
            ],
        )
        st.pydeck_chart(deck, width=800)
    else:
        st.error("Address not found. Try a more specific address.")

st.write("")
if st.button("Calculate price", type="primary"):
    if lat is None or lon is None:
        st.error("Please enter a valid address first.")
    else:
        try:
            input_data = {
                'area': area,
                'rooms': rooms,
                'floor': floor,
                'floors': floors,
                'building_type': building_type,
                'heating': heating,
                'furnishing': furnishing,
                'latitude': lat,
                'longitude': lon
            }

            for option in feature_options:
                feature = option["input_name"]
                input_data[feature] = 1 if feature in selected_features else 0

            input_df = pd.DataFrame([input_data])

            building_info = pd.read_csv('./data/building_info.csv')
            trip_statistics = pd.read_csv('./data/trip_statistics.csv')

            address_data = pd.merge(building_info, trip_statistics, left_on=['longitude', 'latitude'], right_on=['origin_lon', 'origin_lat'], how='left')

            distance = cdist(
                input_df[['latitude', 'longitude']],
                address_data[['latitude', 'longitude']],
                metric='euclidean'
            )

            address_info_array = address_data[['street', 'houseNo', 'eldership',
                                         'distance_akropolis', 'time_akropolis',
                                         'distance_cathedral', 'time_cathedral',
                                         'distance_kirtimai', 'time_kirtimai',
                                         'distance_shopping_center', 'time_shopping_center',
                                         'distance_train_station', 'time_train_station',
                                         'traffic_noise', 'airport_noise', 'railway_noise',
                                         'heating_score']].to_numpy()[distance.argmin(axis=1)]

            address_info_df = pd.DataFrame(address_info_array, columns=['street', 'house_number', 'eldership',
                                                                         'distance_akropolis', 'time_akropolis',
                                                                         'distance_cathedral', 'time_cathedral',
                                                                         'distance_kirtimai', 'time_kirtimai',
                                                                         'distance_shopping_center', 'time_shopping_center',
                                                                         'distance_train_station', 'time_train_station',
                                                                         'traffic_noise', 'airport_noise', 'railway_noise',
                                                                         'heating_score'])

            input_df['street'] = address_info_df['street'].values[0]
            input_df['house_number'] = address_info_df['house_number'].values[0]
            input_df['eldership'] = address_info_df['eldership'].values[0]
            input_df['time_akropolis'] = address_info_df['time_akropolis'].values[0]
            input_df['time_cathedral'] = address_info_df['time_cathedral'].values[0]
            input_df['time_kirtimai'] = address_info_df['time_kirtimai'].values[0]
            input_df['time_shopping_center'] = address_info_df['time_shopping_center'].values[0]
            input_df['time_train_station'] = address_info_df['time_train_station'].values[0]
            input_df['traffic_noise'] = address_info_df['traffic_noise'].values[0]
            input_df['airport_noise'] = address_info_df['airport_noise'].values[0]
            input_df['railway_noise'] = address_info_df['railway_noise'].values[0]
            input_df['heating_score'] = address_info_df['heating_score'].values[0]


            input_geom = gpd.GeoDataFrame(
                input_df, geometry=gpd.points_from_xy(input_df['longitude'], input_df['latitude']), crs="EPSG:4326"
            )

            input_geom['full_street'] = input_geom['street'] + ' ' + input_geom['house_number']

            population = gpd.read_file('./data/population.json')
            population = population.to_crs(crs='EPSG:4326')

            input_geom = gpd.sjoin(left_df=input_geom, right_df=population[["G2017", "geometry"]], how="left", predicate="intersects")
            if 'index_right' in input_geom.columns:
                input_geom = input_geom.drop(columns=["index_right"])
            input_geom.rename(columns={'G2017':'local_population_2017'}, inplace=True)

            kinder = gpd.read_file('./data/kindergarden.csv')
            kinder = pd.merge(left=kinder, right=building_info, left_on='address', right_on='fullAddress', how='left')
            kinder = gpd.GeoDataFrame(
                kinder, geometry=gpd.points_from_xy(kinder['longitude'], kinder['latitude']), crs="EPSG:4326"
            )
            input_geom = input_geom.assign(distance_kinder = input_geom.apply(lambda row: kinder.distance(row.geometry).min(), axis=1))

            school = gpd.read_file('./data/school.json')
            school = school.to_crs(crs='EPSG:4326')
            input_geom = input_geom.assign(distance_school = input_geom.apply(lambda row: school.distance(row.geometry).min(), axis=1))

            stops = gpd.read_file('./data/bus_stops.json')
            stops = stops.to_crs(crs='EPSG:4326')
            input_geom = input_geom.assign(distance_bus_stop = input_geom.apply(lambda row: stops.distance(row.geometry).min(), axis=1))

            crimes = gpd.read_file("./data/crime_data/GRID500.shp").to_crs(crs='EPSG:4326')
            crimes = crimes[crimes['PERIOD'] == 'M']

            input_geom = gpd.sjoin(left_df=input_geom, right_df=crimes[["VISI", "geometry"]], how="left", predicate="intersects")
            if 'index_right' in input_geom.columns:
                input_geom = input_geom.drop(columns=["index_right"])
            input_geom.rename(columns={'VISI':'crimes_2024'}, inplace=True)
            
            columns_to_drop = ['geometry']
            if 'full_street' in input_geom.columns:
                columns_to_drop.append('full_street')
            
            input_for_prediction = input_geom.drop(columns=columns_to_drop)
            
            categorical_cols = ['building_type', 'heating', 'furnishing', 'street', 'eldership', 
                              'traffic_noise', 'railway_noise', 'airport_noise']
            for col in categorical_cols:
                if col in input_for_prediction.columns:
                    input_for_prediction[col] = input_for_prediction[col].astype(str)
            
            input_for_prediction = pd.get_dummies(input_for_prediction, columns=categorical_cols, drop_first=False)
            
            if hasattr(model, 'feature_names_in_'):
                expected_features = model.feature_names_in_
                
                for feature in expected_features:
                    if feature not in input_for_prediction.columns:
                        input_for_prediction[feature] = 0
                
                extra_features = set(input_for_prediction.columns) - set(expected_features)
                if extra_features:
                    input_for_prediction = input_for_prediction.drop(columns=list(extra_features))
                
                input_for_prediction = input_for_prediction[expected_features]
            else:
                st.warning("Model doesn't have feature_names_in_ attribute. Attempting prediction with current features.")
            
            prediction = np.exp(model.predict(input_for_prediction)[0])
            st.metric(label="Estimated Value", value=f"{round(prediction):,} €".replace(",", " "))
            if not selected_features:
                st.warning("Warning: No relevant features were selected. Price might be inaccurate.")
            st.balloons()
            
        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")
            st.write("Please ensure all fields are filled correctly.")
            import traceback
            st.text(traceback.format_exc())


st.markdown(
    """
    <hr style="margin-top: 3rem; margin-bottom: 1rem;">
    <div style="text-align: center; color: gray; font-size: 0.9em;">
        Built by <b>Mykolas Motiejūnas</b> · 
        <a href="https://github.com/Mykolazaz" target="_blank">
            GitHub
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)