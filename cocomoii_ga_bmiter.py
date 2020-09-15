# -*- coding: utf-8 -*-
"""COCOMOII_ga_bmiter.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1l4OOAWNn76maUl3N9qqqYPC8W6nfbcB8
"""

# import libraries
import numpy as np
import pandas as pd
import math
from google.colab import files
import io

uploaded = files.upload()

# reading dataset
cocomo_data = pd.read_csv(io.StringIO(uploaded['cocomo2_dataset.csv'].decode('utf-8')))

# storing the data required
# actual effort for each project
act_eff = np.array(cocomo_data['ACT_EFFORT'])
act_eff = act_eff[:10]
# scale factors
SF = np.array(cocomo_data.iloc[:10, 3:8])
# effort multipliers
EM = np.array(cocomo_data.iloc[:10, 8:25])
# size of projects
size = np.array(cocomo_data['Physical Delivered KLOC'])
size = size[:10]
fitness = np.empty(len(size))

# selection process
def select_mating_pool(pop, fitness, num_parents):
    # Selecting the best individuals in the current generation as parents for producing the offspring of the next generation.
    parents = np.empty((num_parents, pop.shape[1]))
    for parent_num in range(num_parents):
        max_fitness_idx = np.where(fitness == np.max(fitness))
        max_fitness_idx = max_fitness_idx[0][0]
        parents[parent_num, :] = pop[max_fitness_idx, :]

    return parents

# crossover process
def crossover(parents, offspring_size):
    offspring = np.empty(offspring_size)
    # The point at which crossover takes place between two parents. Usually, it is at the center.
    crossover_point = np.uint8(offspring_size[1]/2)
    for k in range(offspring_size[0]):
        # Index of the first parent to mate.
        parent1_idx = k%parents.shape[0]
        # Index of the second parent to mate.
        parent2_idx = (k+1)%parents.shape[0]
        # The new offspring will have its first half of its genes taken from the first parent.
        offspring[k, 0:crossover_point] = parents[parent1_idx, 0:crossover_point]
        # The new offspring will have its second half of its genes taken from the second parent.
        offspring[k, crossover_point:] = parents[parent2_idx, crossover_point:]
    return offspring

# Number of the Coefff we are looking to optimize.
num_coeff = 2
# defining max number of task solutions 
sol_per_pop = 10
# Defining the population size.
pop_size = (sol_per_pop, num_coeff) # The population will have sol_per_pop chromosome where each chromosome has num_weights genes.
#Creating the initial population.
new_population_B = np.random.uniform(low=0.88, high=0.94, size=10)
new_population_A = np.random.uniform(low=2.90, high=2.96, size=10)
new_population = np.stack((new_population_B, new_population_A), axis = 1)

# Performing Genetic algorithm
better_fitness, f = 0, 0
num_iterations = 0
num_parents_mating = 2
while(better_fitness>=f and num_iterations<100):
    # Measuring the fitness of each chromosome in the population.
    num_iterations += 1
    f = better_fitness
    avg_fitness = np.empty(len(size))
    for i in range(len(new_population)):
        for j in range(len(size)):
            E = new_population[i][0]+0.01*sum(SF[j])
            em_prod = 1
            for num in EM[j]:
              em_prod*=num
            PM = new_population[i][1] * math.pow(size[j], E) * em_prod
            fitness[j] = (act_eff[j]-PM)/act_eff[j]
        avg_fitness[j] = sum(fitness)/len(fitness)
    better_fitness = max(avg_fitness)
    # Selecting the best parents in the population for mating.
    parents = select_mating_pool(new_population, avg_fitness, num_parents_mating)
 
    # Generating next generation using crossover.
    offspring_crossover = crossover(parents, offspring_size=(pop_size[0]-parents.shape[0], num_coeff))
 
    # Adding some variations to the offsrping using mutation.
    offspring_mutation = mutation(offspring_crossover)
    # Creating the new population based on the parents and offspring.
    new_population[0:parents.shape[0], :] = parents
    new_population[parents.shape[0]:, :] = offspring_mutation

# solution corresponding to the best fitness
best_match_idx = np.where(fitness == np.max(fitness))
print("Best value for B : ", new_population[best_match_idx, :][0][0][0])
print("Best value for A : ", abs(new_population[best_match_idx, :][0][0][1]))