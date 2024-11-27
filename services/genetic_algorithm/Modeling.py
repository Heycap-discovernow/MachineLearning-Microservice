import math 
import random
import os
import requests
import polyline
from dotenv import load_dotenv

load_dotenv()

class Model:    
    api_key = os.getenv("API_KEY")
    @staticmethod
    def get_parameters(origin, target, transport):
        distance = Model.get_distance(origin, target)
        travel_time = Model.calculate_travel_time(distance, transport)
        travel_cost = Model.travel_cost(distance, transport, travel_time)
        return {
                'distance': distance,
                'travel_time': travel_time,
                'travel_cost': travel_cost
        }
        
    @staticmethod
    def get_distance(current_poi, next_poi): #Obtiene la distancia entre dos puntos usando la formula de Haversine
        current_lat, current_long = float(current_poi[0]), float(current_poi[1])
        next_lat, next_long = float(next_poi[0]), float(next_poi[1])
        
        R = 6371  # Radio de la Tierra en km
        lat1, lon1 = math.radians(current_lat), math.radians(current_long)
        lat2, lon2 = math.radians(next_lat), math.radians(next_long)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        return round(distance, 5)

    @staticmethod
    def sort_by_proximity(route): #Ordena la ruta basandose en la proximidad geografica de los puntos de interes
        unique_route = Model.filter_route(route)
        if len(unique_route) == 0:
            raise ValueError("No pudimos encontrar una ruta con los parametros proporcionados, por favor incrementa un poco los valores o intenta de nuevo.")
        sorted_route = [unique_route[0]]  # Mantén el punto de inicio
        remaining = unique_route[1:]
        while remaining:
            last_poi = sorted_route[-1]['target_coord'] # Selección del último punto de interés añadido. [-1] selecciona el último elemento de la lista porque los indices negativos cuentan desde el final.
            next_poi = min(remaining, key=lambda x, last_poi=last_poi: Model.get_distance(last_poi, x['target_coord'])) # Calcula la distancia entre last_poi y cada punto de interes restante, y selecciona el más cercano.
            sorted_route.append(next_poi)
            remaining.remove(next_poi)
        return sorted_route # Esta implementación asegura que la ruta se optimiza en términos de distancia entre puntos consecutivos
    
    @staticmethod
    def filter_route(route):
        seen = set()
        unique_route = []
        for segment in route:
            if segment['target_coord'] not in seen:
                unique_route.append(segment)
                seen.add(segment['target_coord'])
        
        return unique_route

    @staticmethod
    def calculate_travel_time(distance, transport):
        average_speeds = {
            'car': 60,
            'bike': 15,
            'walk': 5,
            'bus': 20
        }
        
        speed = average_speeds.get(transport, 20)
        time_in_hours = distance / speed
        time_in_minutes = time_in_hours * 60
        return round(time_in_minutes, 2)
    
    @staticmethod
    def total_time(travel_time, visit_time):
        return travel_time + visit_time
    
    @staticmethod
    def cost_visit(range_cost):
        range_cost = int(range_cost)
        if (range_cost == 0):
            return random.randrange(50, 250)
        elif (range_cost == 1):
            return random.randrange(250, 450)
        elif (range_cost == 2):
            return random.randrange(450, 650)
        elif (range_cost == 3):
            return random.randrange(650, 1000)
        else:
            return random.randrange(1000, 2000)
    
    @staticmethod
    def travel_cost(distance, transport, travel_time):
        if transport == 'car':
            base_fee = 35
            fee_km = 7
            fee_min = 3.5
            total_cost = base_fee + (distance * fee_km) + (travel_time * fee_min)
            return total_cost 
        elif transport == 'bus':
            return 10
        else:
            return 0
    
    @staticmethod
    def total_cost(travel_cost, cost_visit):
        return travel_cost + cost_visit
    
    @staticmethod
    def get_polyline(coordinates):
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": Model.api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"
        }

        origin = {"location": {"latLng": {"latitude": coordinates[0][0], "longitude": coordinates[0][1]}}}
        destination = {"location": {"latLng": {"latitude": coordinates[-1][0], "longitude": coordinates[-1][1]}}}
        intermediates = [{"location": {"latLng": {"latitude": lat, "longitude": lng}}} for lat, lng in coordinates[1:-1]]

        payload = {
            "origin": origin,
            "destination": destination,
            "intermediates": intermediates,
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE_OPTIMAL",
            "polylineQuality": "HIGH_QUALITY",
            "computeAlternativeRoutes": False,
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False
            },
            "languageCode": "en-US"
        }

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if "routes" in data and len(data["routes"]) > 0:
                route = data["routes"][0]
                polyline_encoded = route["polyline"]["encodedPolyline"]  # Polilínea codificada
                
                return polyline_encoded
            else:
                print("Error: La respuesta no contiene las rutas esperadas.")
                return None
        else:
            print("Error al obtener la ruta:", response.status_code, response.text)
            return None