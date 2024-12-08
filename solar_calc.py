import math
import requests
import json
import random
from shapely.geometry import Point, Polygon  # Biblioteka do pracy z geometrią

json_data_arr = []
yearly_value_arr = []

def clear_arr():
    json_data_arr.clear()
    yearly_value_arr.clear()

def move_point(lat: float, lon: float, distance_km: float = 5/1000, direction: str = 'C'):
    """Move point function for specific direction."""
    R = 6371  # Promień Ziemi w kilometrach
    delta = distance_km / R  # Odległość w radianach

    # Zamiana stopni na radiany
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    if direction == 'C':
        new_lat = lat_rad
        new_lon = lon_rad
    elif direction == 'N':  # Północ
        new_lat = lat_rad + delta
        new_lon = lon_rad
    elif direction == 'S':  # Południe
        new_lat = lat_rad - delta
        new_lon = lon_rad
    elif direction == 'E':  # Wschód
        new_lat = lat_rad
        new_lon = lon_rad + delta / math.cos(lat_rad)
    elif direction == 'W':  # Zachód
        new_lat = lat_rad
        new_lon = lon_rad - delta / math.cos(lat_rad)
    else:
        raise ValueError("Nieprawidłowy kierunek!")

    # Zamiana wyników na stopnie
    new_lat_deg = math.degrees(new_lat)
    new_lon_deg = math.degrees(new_lon)
    return new_lat_deg, new_lon_deg

def get_points_in_polygon(polygon_coords, distance_km: float = 0.001, num_points: int = 100):
    """
    Funkcja generuje `num_points` punktów wewnątrz zadanego poligonu.
    """
    point_arr = []
    polygon = Polygon(polygon_coords)  # Tworzymy obiekt poligonu z listy współrzędnych

    min_lon, min_lat, max_lon, max_lat = polygon.bounds  # Ustalamy bounding box

    # Generujemy punkty wewnątrz bounding boxa, sprawdzając, czy należą do poligonu
    for _ in range(num_points):
        while True:
            random_lat = min_lat + (max_lat - min_lat) * random.random()
            random_lon = min_lon + (max_lon - min_lon) * random.random()
            point = Point(random_lon, random_lat)

            if polygon.contains(point):  # Sprawdzamy, czy punkt leży wewnątrz poligonu
                point_arr.append((random_lat, random_lon))
                break

    return point_arr

def calc_year_solar_power_in_polygon(polygon_coords, num_points: int = 100):
    """
    Generujemy punkty w obszarze poligonu, a następnie obliczamy roczną moc słoneczną dla każdego punktu.
    """
    clear_arr()
    points_arr = get_points_in_polygon(polygon_coords, num_points=num_points)

    # Iterujemy po wszystkich punktach w obrębie poligonu
    for i, (lat, lon) in enumerate(points_arr):
        try:
            url = update_link(lat, lon)
            response = requests.get(url)

            if response.status_code == 200:
                json_data = response.json()
                json_data_arr.append(json_data)
            else:
                print(f"[ERROR] Błąd odpowiedzi z API dla punktu {i}: {response.status_code}, współrzędne: ({lat}, {lon})")
        except Exception as e:
            print(f"[ERROR] Wyjątek dla punktu {i}: {e}, współrzędne: ({lat}, {lon})")


# Zbieramy wyniki
    for json_data in json_data_arr:
        try:
            yearly_value_arr.append(json_data['outputs']['totals']['fixed']['E_y'])
        except KeyError as e:
            print(f"[ERROR] Błąd w danych JSON: {e}")

def get_heat_points_in_polygon(polygon_coords, num_points: int = 100):
    """
    Funkcja generuje punkty heatmapy tylko dla punktów wewnątrz poligonu.
    """
    calc_year_solar_power_in_polygon(polygon_coords, num_points)

    heat_points_arr = []
    for i, (lat, lon) in enumerate(get_points_in_polygon(polygon_coords, num_points)):
        if i < len(yearly_value_arr):
            heat_points_arr.append([lat, lon, yearly_value_arr[i]])

    return heat_points_arr

def update_link(lat_deg: float, lon_deg: float):
    """Update API link with given coordinates."""
    url = "https://re.jrc.ec.europa.eu/api/v5_3/PVcalc?lat=XXX&lon=YYY&raddatabase=PVGIS-SARAH3&browser=1&userhorizon=&usehorizon=1&outputformat=json&js=1&select_database_grid=PVGIS-SARAH3&pvtechchoice=crystSi&peakpower=1&loss=14&mountingplace=free&angle=35&aspect=0"
    url = url.replace("XXX", str(lat_deg))
    url = url.replace("YYY", str(lon_deg))
    return url

