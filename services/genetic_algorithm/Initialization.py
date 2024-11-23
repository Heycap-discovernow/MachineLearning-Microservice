import random
from services.genetic_algorithm.Modeling import Model as md

class Initialization:
    def __init__(self, places, hours, quote=500):
        self.places = places
        self.time_max = 60 * int(hours)
        self.quote = float(quote)
        self.start_place = places[0]
        self.cache = {}
        self.individual_cache = {}

    def generate_population(self, p0=50):
        population = []
        for _ in range(p0):
            route = [self.start_place]
            available_pois = self.places[1:]
            individual = []

            while available_pois:
                # Encuentra el POI más cercano al último POI en la ruta
                current_poi = route[-1]
                distances = [(poi, md.get_distance((current_poi['lat'], current_poi['lon']), (poi['lat'], poi['lon']))) for poi in available_pois]
                next_poi = min(distances, key=lambda x: x[1])[0]
                route.append(next_poi)
                available_pois.remove(next_poi)
                transport = random.choice(["car", "walk", "bus"])
                individual.append({
                    'origin_name': current_poi['name'],
                    'origin_coord': (current_poi['lat'], current_poi['lon']),
                    'time_visit': int(current_poi['time']) if current_poi['time'] is not None else random.choice([30, 60, 90, 120, 150, 180, 210, 240, 270, 300]),
                    'cost_visit': md.cost_visit(current_poi['cost']),
                    'target_name': next_poi['name'],
                    'target_coord': (next_poi['lat'], next_poi['lon']),
                    'transport': transport
                })

            # Cada individuo en la poblacion es una lista de diccionarios, donde cada diccionario representa un segmento de la ruta
            population.append(individual)
            
        return population

    def fitness(self, population):
        population_with_fitness = []
        attempts = 0
        for individual in population:
            # Convierte el individual a una tupla para usarla como clave de caché
            individual_key = tuple((poi['origin_coord'], poi['target_coord'], poi['transport']) for poi in individual)
            if individual_key in self.individual_cache:
                fitness_data = self.individual_cache[individual_key]
            else:
                total_distance = 0
                total_time = 0
                total_cost = 0

                # Ordenar la ruta por proximidad geográfica
                individual = md.sort_by_proximity(individual) # Ayuda al algoritmo a encontrar soluciones mas optimaz y logicas

                for coord in individual: #itera sobre todos los segmentos de la ruta, sumando la distancia, tiempo y costo de cada segmento para obtener los totales de la ruta completa.
                    origin_coord = coord['origin_coord']
                    target_coord = coord['target_coord']
                    transport = coord['transport']

                    # Crear una clave única para la caché
                    cache_key = (origin_coord, target_coord, transport)

                    if cache_key in self.cache:
                        info = self.cache[cache_key]
                    else:
                        info = md.get_parameters(origin_coord, target_coord, transport)
                        self.cache[cache_key] = info

                    if info is not None:
                        total_distance += info['distance']
                        total_time += md.total_time(info['travel_time'], coord['time_visit'])
                        total_cost += md.total_cost(info['travel_cost'], coord['cost_visit'])
                    else:
                        # Penalizar rutas no encontradas
                        total_time += 999
                        total_cost += 999
                
                # Se invierte la relación porque queremos que las rutas con menor distancia, tiempo y costo sean consideradas mejores
                fitness_value = (1 / (1 + total_distance)) + (1 / (1 + total_time)) + (1 / (1 + total_cost)) # o sea que valores más bajos resultan en valores más altos de aptitud.
                # La suma de los tres componentes me permite considerar estas 3 variables simultáneamente en la evaluación de la ruta.
                # fitness_value = 0.5*(1 / (1 + total_distance)) + 5*(1 / (1 + total_time)) + 2*(1 / (1 + total_cost)) # o sea que valores más bajos resultan en valores más altos de aptitud.
                # dar más peso a un factor específico, aumenta la importancia de ese factor en la evaluación.
                
                if not total_time <= self.time_max or not total_cost <= self.quote: # Si el tiempo total o el costo total no es menor o igual que la cotización y el tiempo maximo permitido, penaliza la ruta
                    last_poi = individual[-1]
                    individual.remove(last_poi)


                fitness_data = {
                    'route': individual,
                    'fitness': fitness_value,
                    'distance': total_distance,
                    'time': total_time,
                    'cost': total_cost
                }

                # Almacenar el resultado en la caché de individual
                self.individual_cache[individual_key] = fitness_data

            population_with_fitness.append(fitness_data)

        return population_with_fitness