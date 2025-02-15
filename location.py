import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import pandas as pd
import requests
import folium
from streamlit_folium import folium_static

def get_nearby_venues(latitude, longitude, radius, keyword, place_type):
    """
    Get nearby venues from the RapidAPI endpoint.
    """
    url = "https://google-map-places.p.rapidapi.com/maps/api/place/nearbysearch/json"

    querystring = {
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "keyword": keyword,
        "type": place_type
    }


    headers = {
    'x-rapidapi-key': "fb87524ac1msh25340f913b14344p10f764jsn7c399ee9b066",
    'x-rapidapi-host': "google-map-places.p.rapidapi.com"
    
    }
    # response =conn.request("GET", "/maps/api/geocode/json?address=1600%20Amphitheatre%2BParkway%2C%20Mountain%20View%2C%20CA&language=en&region=en&result_type=administrative_area_level_1&location_type=APPROXIMATE", headers=headers)
    response = requests.get(url, headers=headers, params=querystring)
    print(response)
    if response.status_code == 200:
        data = response.json()
        venues = []
        for result in data.get("results", [])[:10]:  # Limiting to 5 results
            venue = {
                "name": result["name"],
                "latitude": result["geometry"]["location"]["lat"],
                "longitude": result["geometry"]["location"]["lng"],
                "rating": result.get("rating", None),
                "address": result.get("vicinity", "")
            }
            venues.append(venue)
        #st.write(venues)
        return venues
    else:
        st.error("Failed to fetch nearby venues.")
        return []
        
def locate():
    st.title("Find Nearby Veterinary Clinics")
    st.write("Recommended to use Edge browser")

    # Get user's location
    location = streamlit_geolocation()

    if location:
        latitude = location.get("latitude")
        longitude = location.get("longitude")

        if latitude is not None and longitude is not None:
            st.write(f"Your current location: Latitude {latitude}, Longitude {longitude}")

            # Fetch nearby places using RapidAPI
            radius = 5000  # meters
            keyword = "veterinary"
            place_type = "veterinary_clinic"
            nearby_places = get_nearby_venues(latitude, longitude, radius, keyword, place_type)

            if not nearby_places:  # Check if the API returned empty results
                st.warning("No nearby veterinary clinics found.")
                return

            # Create a DataFrame with nearby places
            places_df = pd.DataFrame(nearby_places)

            # Ensure 'name' column exists
            if "name" not in places_df.columns:
                st.error("Unexpected API response format. 'name' column missing.")
                st.write(places_df)  # Print DataFrame for debugging
                return

            # Add dropdown to select clinic
            selected_clinic = st.selectbox("Select a clinic:", places_df["name"])

            if selected_clinic:
                # Get the location of the selected clinic
                selected_clinic_location = places_df[places_df["name"] == selected_clinic]
                selected_clinic_latitude = selected_clinic_location.iloc[0]["latitude"]
                selected_clinic_longitude = selected_clinic_location.iloc[0]["longitude"]

                # Display selected clinic details
                st.write("Selected Clinic Details:")
                selected_clinic_details = {
                    "Name": selected_clinic,
                    "Rating": selected_clinic_location.iloc[0]["rating"],
                    "Address": selected_clinic_location.iloc[0]["address"]
                }
                st.dataframe(pd.DataFrame(selected_clinic_details, index=[1]))

                # Create a Folium map with user's location, and selected clinic
                map_center = (latitude, longitude)
                my_map = folium.Map(location=map_center, zoom_start=13)

                # Add marker for user's location
                folium.Marker(location=map_center,
                            popup="Your Location",
                            icon=folium.Icon(color="green", icon="user")).add_to(my_map)

                # Add marker for selected clinic
                folium.Marker(location=[selected_clinic_latitude, selected_clinic_longitude],
                                popup=selected_clinic,
                                icon=folium.Icon(color="red", icon="star")).add_to(my_map)

                # Add polyline between user's location and selected clinic
                polyline = folium.PolyLine(locations=[map_center, (selected_clinic_latitude, selected_clinic_longitude)],
                                        color='blue')
                my_map.add_child(polyline)

                # Display the map
                folium_static(my_map)

        else:
            st.write("Unable to retrieve latitude and longitude.")
    else:
        st.write("Unable to retrieve location.")
