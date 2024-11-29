""" 
This script implements a genetic algorithm for solving the 3D bin-packing problem, 
including constraints such as weight stability, package priorities, and cost optimization. 
The output format includes total cost, total packages packed, and ULD details. 
"""

import random

class Package:
    """ Represents a package to be loaded into a ULD. """
    def __init__(self, pkg_id, length, width, height, weight, priority, cost_delay):
        self.id = pkg_id  # Renamed from 'id' to 'pkg_id'
        self.length = length
        self.width = width
        self.height = height
        self.weight = weight
        self.priority = priority
        self.cost_delay = cost_delay
        self.position = None  # Coordinates (x0, y0, z0, x1, y1, z1)
        self.placed = False  # Tracks if the package is placed
        self.uld_id = "NONE"  # Default ULD ID if not placed

class ULD:
    """ Represents a Unit Load Device (ULD) for packing packages. """
    def __init__(self, uld_id, length, width, height, weight_limit):
        self.id = uld_id  # Renamed from 'id' to 'uld_id'
        self.length = length
        self.width = width
        self.height = height
        self.weight_limit = weight_limit
        self.packages = []  # List of packages in this ULD
        self.total_weight = 0  # Current total weight of ULD

    def can_fit(self, package):
        """ Checks if a package can be placed in the ULD. """
        return (self.total_weight + package.weight <= self.weight_limit and 
                package.length <= self.length and 
                package.width <= self.width and 
                package.height <= self.height)

    def add_package(self, package, position):
        """ Adds a package to the ULD if it fits. """
        if self.can_fit(package):
            self.packages.append(package)
            self.total_weight += package.weight
            package.placed = True
            package.uld_id = self.id
            package.position = (position[0], position[1], position[2],  # x0, y0, z0
                    position[0] + package.length,           # x1 = x0 + length
                    position[1] + package.width,            # y1 = y0 + width
                    position[2] + package.height)           # z1 = z0 + height

            return True
        return False

def fitness_function(ulds, packages):
    """ Calculates the fitness score of a solution. """
    fitness_score = 0
    weight_penalty = 0
    stability_penalty = 0
    unplaced_packages_penalty = 0
    priority_spread_penalty = 0

    num_priority_uld = sum(1 for uld in ulds if any(pkg.priority for pkg in uld.packages))
    unplaced_economy_packages = sum(1 for pkg in packages if not pkg.placed and not pkg.priority)

    for uld in ulds:
        # Penalize weight violations
        if uld.total_weight > uld.weight_limit:
            weight_penalty += (uld.total_weight - uld.weight_limit) * 10
            
        # Check stability for each package in uld.packages:
        for package in uld.packages:
            if not is_stable(package, uld):
                stability_penalty += 1

    # Penalty for unplaced Economy Packages
    unplaced_packages_penalty = 50 * unplaced_economy_packages
    
    # Penalty for spreading Priority Packages
    if num_priority_uld > 1:
        priority_spread_penalty = 5000 * num_priority_uld

    # Combine penalties into fitness score
    fitness_score -= weight_penalty
    fitness_score -= stability_penalty * 5
    fitness_score -= unplaced_packages_penalty
    fitness_score -= priority_spread_penalty
    
    return fitness_score

def is_stable(package, uld):
    """ Checks if a package is stably placed within a ULD. """
    for other_package in uld.packages:
        if package.position and other_package.position:
            if (package.position[2] > other_package.position[2] and 
                package.weight > other_package.weight):
                return False
    return True

def create_initial_population(ulds, packages, population_size):
    """ Creates the initial population for the genetic algorithm. """
    population = []
    
    for _ in range(population_size):
        random.shuffle(packages)
        solution = []
        
        for uld in ulds:
            for package in packages:
                uld.add_package(package, position=(0, 0, 0))  # Simplified placement
                
            solution.append(uld)
        
        population.append(solution)
    
    return population

def generate_output(ulds, packages):
    """ Generates the final output in the required format. """
    total_cost = -fitness_function(ulds, packages)
    total_packed = sum(1 for pkg in packages if pkg.placed)
    num_priority_uld = sum(1 for uld in ulds if any(pkg.priority for pkg in uld.packages))

    output_lines = [f"{total_cost},{total_packed},{num_priority_uld}"]
    
    for pkg in packages:
        if pkg.placed:
            x0, y0, z0, x1, y1, z1 = pkg.position
            output_lines.append(f"{pkg.id},{pkg.uld_id},{x0},{y0},{z0},{x1},{y1},{z1}")
        else:
            output_lines.append(f"{pkg.id},NONE,-1,-1,-1,-1,-1,-1")
    
    return "\n".join(output_lines)

if __name__ == "__main__":
    ulds_data = [
        ULD("U1", 224, 318, 162, 2500),
        ULD("U2", 244, 318, 244, 2800)
    ]
    
    packages_data = [
        Package("P-1", 50, 50, 50, 20, False, 100),
        Package("P-2", 70, 60, 60, 30, True, None),
        Package("P-3", 100, 100, 50, 50, False, 200),
        Package("P-4", 30, 30, 30, 10, True, None)
    ]
    
    best_solution = create_initial_population(ulds_data, packages_data, 10)
    output_result = generate_output(ulds_data, packages_data)
    print(output_result)

    ulds_data = [  # Renamed from 'uld_list' to 'ulds_data'
        ULD("U1", 224, 318, 162, 2500),
        ULD("U2", 224, 318, 162, 2500),
        ULD("U3", 244, 318, 244, 2800),
        ULD("U4", 244, 318, 244, 2800),
        ULD("U5", 244, 318, 285, 3500),
        ULD("U6", 244, 318, 285, 3500),
    ]
    
    packages_data = [  # Renamed from 'package_list' to 'packages_data'
        Package("P-1", 99, 53, 55, 61, False, 176),
        Package("P-2", 56, 99, 81, 53, True, None),
        # Add all packages here...
    ]
    
    best_solution = create_initial_population(ulds_data, packages_data, 50)
    
    output_result = generate_output(ulds_data, packages_data)
    
    print(output_result)