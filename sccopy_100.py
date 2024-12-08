import math
import requests
import json

json_data_arr = []
yearly_value_arr = []

script_log_arr = []

def clear_arr():
    json_data_arr.clear()
    yearly_value_arr.clear()

# Funkcja do obliczania sąsiednich punktów geograficznych
def move_point(lat: float, lon: float, distance_km: int, direction: str = 'C'):
    # Stałe
    R = 6371  # Promień Ziemi w kilometrach
    delta = distance_km / R  # Odległość w radianach

    script_log_arr.append(f"[MOVE_POINT]: Obliczanie punktu w kierunku: {direction}.")

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

    script_log_arr.append(f"[MOVE_POINT]: Obliczono punkt: {new_lat_deg:.2f}, {new_lon_deg:.2f}.")
    return new_lat_deg, new_lon_deg

def get_points(lat_deg: float, lon_deg: float, distance_km: int = 1, num_points: int = 100):
    """
    Funkcja generuje `num_points` punktów wokół zadanych współrzędnych.
    """
    point_arr = []
    script_log_arr.append(f"[GET_POINTS]: Dodawanie punktów. Liczba punktów: {num_points}")

    # Używamy siatki wokół punktu środkowego, tworząc num_points punktów
    # Tworzymy siatkę, np. 10 x 10 punktów wokoło
    grid_size = int(math.sqrt(num_points))  # Siatka 10x10 da 100 punktów

    for i in range(grid_size):
        for j in range(grid_size):
            # Przesunięcie punktów w zależności od i, j
            lat_offset = (i - grid_size // 2) * (distance_km / grid_size)
            lon_offset = (j - grid_size // 2) * (distance_km / grid_size)

            new_point = move_point(lat_deg + lat_offset, lon_deg + lon_offset, distance_km)
            point_arr.append(new_point)

    script_log_arr.append(f"[GET_POINTS]: Dodano punkty: {point_arr}")
    return point_arr

def calc_year_solar_power(lat_deg: float, lon_deg: float, distance_km: int = 1, num_points: int = 100):
    clear_arr()

    # Generowanie 100 punktów
    points_arr = get_points(lat_deg, lon_deg, distance_km, num_points)

    # Iterowanie po wszystkich punktach
    for i in range(len(points_arr)):
        try:
            url = update_link(points_arr[i][0], points_arr[i][1])
            response = requests.get(url)

            if response.status_code == 200:
                json_data = response.json()
                json_data_arr.append(json_data)
                script_log_arr.append(f"[GET_YEAR_SOLAR_POWER]: Dodano plik JSON dla punktu {i}: {response}")
            else:
                script_log_arr.append(f"[GET_YEAR_SOLAR_POWER]: Błąd odpowiedzi z API: {response.status_code}")
        except Exception as e:
            script_log_arr.append(f"[GET_YEAR_SOLAR_POWER]: Wystąpił wyjątek dla punktu {i}: {e}")

    # Zbieranie wyników
    for json_data in json_data_arr:
        try:
            yearly_value_arr.append(json_data['outputs']['totals']['fixed']['E_y'])
            script_log_arr.append(
                f"[GET_YEAR_SOLAR_POWER]: Wyciągnięto dane ['E_y']: {json_data['outputs']['totals']['fixed']['E_y']}")
        except KeyError as e:
            script_log_arr.append(f"[GET_YEAR_SOLAR_POWER]: Błąd w danych JSON: {e}")


def get_avg_area_Ey(lat_deg: float, lon_deg: float, distance_km: int = 1):
    calc_year_solar_power(lat_deg, lon_deg, distance_km)

    average: float = sum(yearly_value_arr) / len(yearly_value_arr)
    return average

def update_link(lat_deg: float, lon_deg: float):
    url = "https://re.jrc.ec.europa.eu/api/v5_3/PVcalc?lat=XXX&lon=YYY&raddatabase=PVGIS-SARAH3&browser=1&userhorizon=&usehorizon=1&outputformat=json&js=1&select_database_grid=PVGIS-SARAH3&pvtechchoice=crystSi&peakpower=1&loss=14&mountingplace=free&angle=35&aspect=0"
    url = url.replace("XXX", str(lat_deg))
    url = url.replace("YYY", str(lon_deg))
    return url

def get_heat_points(lat_deg, lon_deg, distance_km=1):
    heat_points_arr = []
    heat_points = []
    points = get_points(lat_deg, lon_deg, distance_km)
    for i in range(100):
        heat_points.append(points[i][0])
        heat_points.append(points[i][1])
        heat_points.append(yearly_value_arr[i])
        heat_points_arr.append(heat_points)
        heat_points = []
    return heat_points_arr
