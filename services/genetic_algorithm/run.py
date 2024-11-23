from services.genetic_algorithm.Initialization import Initialization
from services.genetic_algorithm.Optimization import Optimization

@staticmethod
def ag_service(places, hours, quote, generation=40):
    init = Initialization(places, hours, quote)
    opt = Optimization()
    bests_by_generation = []

    population = init.generate_population()
    fitness_results = init.fitness(population)
    best_route = max(fitness_results, key=lambda x: x['fitness'])
    bests_by_generation.append(best_route)
    
    for _ in range(generation):
        selected = opt.selection(fitness_results)
        children = opt.crossover(selected)
        children = opt.mutation(children)
        new_population = list(population) + list(children)
        fitness_results = init.fitness(new_population)
        best_route = max(fitness_results, key=lambda x: x['fitness'])
        population, currently_best = opt.poda(fitness_results)
        
        if currently_best['fitness'] > best_route['fitness']:
            best_route = currently_best

        bests_by_generation.append(best_route)
    
    best_route = min(bests_by_generation, key=lambda x: x['fitness'])
    best_route = {
        'route': best_route['route'],
        "total_time": round(best_route['time'] / 60, 2),
        'total_cost': round(best_route['cost'], 2)
    }
    return best_route