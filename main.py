import folium
from geopy.geocoders import Nominatim
import csv
import pandas as pd
import math

def year_list(year):
    df = pd.read_csv('location.csv')
    df.columns = ['location', 'name', 'year']
    df = df[df['year'] == str(year)]
    if df.shape[0] > 50:
        return df[:50]
    return df

def add_location(year):
    df = year_list(year)
    lst = list(df['location'])
    lat_lst = []
    lon_lst = []
    coordinates = []
    for loc in lst:
        geolocator = Nominatim(user_agent='map')
        location = geolocator.geocode(loc)

        if location != None:
            lat_lst.append(location.latitude)
            lon_lst.append(location.longitude)
            coordinates.append([location.latitude, location.longitude])

        else:
            i = df[(df.location == loc)].index
            df = df.drop(i, axis = 0)
            continue

            try:
                i = df[(df.location == loc)].index
                df = df.drop(i, axis = 0)
                continue

            except Exception:
                i = df[(df.location == loc)].index
                df = df.drop(i, axis = 0)                
                continue
    df['lat'] = lat_lst
    df['lon'] = lon_lst
    df['coordinates'] = coordinates
    return df

def find_nearest(coord, year):
    df = add_location(year)
    df_coord = list(df['coordinates'])
    dist  =[]
    for coord2 in df_coord:
        radius = 6371
        phi1 = int(coord[0]) * (math.pi / 180)
        phi2 = int(coord2[0]) * (math.pi / 180)
        delta_phi = math.radians((int(coord2[0]) - int(coord[0])))
        delta_lambda = math.radians((int(coord2[1]) - int(coord[1])) * (math.pi / 180))
        a = math.sin(delta_phi/2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = radius * c
        dist.append(distance)
    df['distance'] = dist
    df = df.sort_values(by = ['distance'])
    if df.shape[0] > 10:
        return df[:10]
    return df

def new_csv(coord):
    df = find_nearest(coord, year)
    df.to_csv("final.csv")

def color_creator(distance):

    if float(distance) < 1000: 
        return "red"

    if 1000 <= float(distance) < 2000:
        return "yellow"

    if 2500 <= float(distance) < 4000:
        return "green"
    return "blue"

def create_map():
    data = pd.read_csv("final.csv", error_bad_lines = False)
    
    coordinates = data['coordinates']
    lat = data['lat']
    lon = data['lon']
    distance = data['distance']
    
    map = folium.Map()
    
    fg = folium.FeatureGroup(name = "pointers")
    fg_dst = folium.FeatureGroup(name = "distance colors")
    
    for lt, ln, distance in zip(lat, lon, distance):
        fg.add_child(folium.Marker(location = [lt, ln], icon = folium.Icon()))
        
        fg_dst.add_child(folium.CircleMarker(location=[lt, ln],
                                        radius=10,
                                        fill_color=color_creator(distance),
                                        color='black',
                                        fill_opacity=0.5))
    
    map.add_child(fg_dst)
    map.add_child(fg)
    map.add_child(folium.LayerControl())
    
    map.save('movies_map.html')

if __name__ == "__main__":
    print("Please enter a year:")
    year = int(input())

    print("Please, enter coordinates(lat, lon):")
    coord = str(input())

    print('Map is generating...')

    year_list(year)
    print("found year...")

    add_location(year)
    print("added location...")

    find_nearest(coord, year)
    print("found nearest locations....")

    print('Please wait...')

    new_csv(coord)
    create_map()

    print('Finished. Please have look at the map movies_map.html')
