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
st.write('This is an app that calculates apartment price based on data gathered from Aruodas.lt.')
st.write('Your data is not collected.')

area = st.number_input("Area, m²")
rooms = st.number_input("Number of rooms", step=1)
floor = st.number_input("Floor", step=1)
floors = st.number_input("Total number of floors", step=1)

building_types = [
    "Mūrinis",
    "Blokinis",
    "Monolitinis",
    "Medinis",
    "Rąstinis",
    "Karkasinis",
    "Skydinis",
    "Kita"
]

building_type = st.selectbox(
    "Select building type",
    options=building_types,
)


heating_options = [
    "Centrinis kolektorinis",
    "Centrinis",
    "Dujinis",
    "Aeroterminis",
    "Elektra",
    "Kietu kuru",
    "Geoterminis",
    "Elektra, aeroterminis",
    "Centrinis, elektra",
    "Centrinis, centrinis kolektorinis",
    "Centrinis kolektorinis, dujinis",
    "Kita"
]

heating = st.selectbox(
    "Select heating type",
    options=heating_options,
)


furnishing_options = [
    "Įrengtas",
    "Dalinė apdaila",
    "Kita",
    "Neįrengtas",
    "Nebaigtas statyti",
]

furnishing = st.selectbox(
    "Select furnishing type",
    options=furnishing_options,
)


feature_labels = {
    "enclosed_courtyard": "Enclosed courtyard",
    "new_electrical_wiring": "New electrical wiring",
    "on_auction": "On auction",
    "separate_toilet_bathroom": "Separate toilet & bathroom",
    "renovated": "Renovated",
    "kitchen_connected_to_living_room": "Kitchen connected to living room",
    "high_ceilings": "High ceilings",
    "attic_apartment": "Attic apartment",
    "internet": "Internet",
    "elevator": "Elevator",
    "multi_level_apartment": "Multi-level apartment",
    "cable_tv": "Cable TV",
    "new_sewerage_system": "New sewerage system",
    "separate_entrance": "Separate entrance",
    "terrace": "Terrace",
    "attic": "Attic",
    "closet": "Closet",
    "sauna": "Sauna",
    "parking_space": "Parking space",
    "basement": "Basement",
    "balcony": "Balcony",
    "storage_room": "Storage room",
    "washing_machine": "Washing machine",
    "fridge": "Fridge",
    "heated_floors": "Heated floors",
    "air_conditioner": "Air conditioner",
    "with_furniture": "With furniture",
    "stove": "Stove",
    "dishwasher": "Dishwasher",
    "fireplace": "Fireplace",
    "bathtub": "Bathtub",
    "recuperation_system": "Recuperation system",
    "shower_cabin": "Shower cabin",
    "kitchen_set": "Kitchen set",
    "plastic_pipes": "Plastic pipes",
    "alarm_system": "Alarm system",
    "security_guard": "Security guard",
    "armored_door": "Armored door",
    "code_locked_stairway": "Code-locked stairway",
    "security_cameras": "Security cameras",
}

selected_labels = st.multiselect(
    "Select all relevant features",
    options=list(feature_labels.values()),
)

selected_features = [
    key for key, label in feature_labels.items()
    if label in selected_labels
]

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

            for feature in feature_labels.keys():
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
            # input_df['distance_akropolis'] = address_info_df['distance_akropolis'].values[0]
            input_df['time_akropolis'] = address_info_df['time_akropolis'].values[0]
            # input_df['distance_cathedral'] = address_info_df['distance_cathedral'].values[0]
            input_df['time_cathedral'] = address_info_df['time_cathedral'].values[0]
            # input_df['distance_kirtimai'] = address_info_df['distance_kirtimai'].values[0]
            input_df['time_kirtimai'] = address_info_df['time_kirtimai'].values[0]
            # input_df['distance_shopping_center'] = address_info_df['distance_shopping_center'].values[0]
            input_df['time_shopping_center'] = address_info_df['time_shopping_center'].values[0]
            # input_df['distance_train_station'] = address_info_df['distance_train_station'].values[0]
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
            st.success(f"Estimated Value: {round(prediction)} €")
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