from services.genetic_algorithm.Initialization import Initialization
from services.genetic_algorithm.Optimization import Optimization

@staticmethod
def ag(start_poi, hours, generation=50):
    init = Initialization( start_poi, hours)
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
    
    return bests_by_generation