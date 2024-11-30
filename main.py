import random

class Package:
    """Represents a package to be loaded into a ULD."""
    def __init__(self, pkg_id, length, width, height, weight, priority, cost_delay):
        self.id = pkg_id
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
    """Represents a Unit Load Device (ULD) for packing packages."""
    
    def __init__(self, uld_id, length, width, height, weight_limit):
        self.id = uld_id
        self.length = length
        self.width = width
        self.height = height
        self.weight_limit = weight_limit
        self.packages = []
        self.total_weight = 0

    def can_fit(self, package):
        """Checks if a package can be placed in the ULD."""
        return (self.total_weight + package.weight <= self.weight_limit and 
                package.length <= self.length and 
                package.width <= self.width and 
                package.height <= self.height)

    def add_package(self, package):
        """Adds a package to the ULD if it fits at a valid position."""
        position = self.find_next_position(package)
        
        if position and self.can_fit(package):
            x0, y0, z0 = position
            package.position = (x0, y0, z0,
                                x0 + package.length,
                                y0 + package.width,
                                z0 + package.height)
            self.packages.append(package)
            self.total_weight += package.weight
            package.placed = True
            package.uld_id = self.id
            return True
        return False

    def find_next_position(self, package):
        """Finds the next available position in the ULD for the package."""
        if not self.packages:
            return (0, 0, 0)  # First package starts at (0, 0, 0)

        for x in range(self.length):
            for y in range(self.width):
                for z in range(self.height):
                    if self.is_position_valid(package, x, y, z):
                        return (x, y, z)

        return None  # No valid position found

    def is_position_valid(self, package, x, y, z):
        """Checks if a package can be placed at (x, y, z) without overlapping."""
        if (x + package.length <= self.length and
            y + package.width <= self.width and
            z + package.height <= self.height):
            for p in self.packages:
                if self.do_packages_overlap(p.position, (x, y, z, 
                                                         x + package.length, 
                                                         y + package.width, 
                                                         z + package.height)):
                    return False
            return True
        return False

    def do_packages_overlap(self, pos1, pos2):
        """Checks if two cuboidal packages overlap in 3D space."""
        x0_1, y0_1, z0_1, x1_1, y1_1, z1_1 = pos1
        x0_2, y0_2, z0_2, x1_2, y1_2, z1_2 = pos2

        return not (x1_1 <= x0_2 or x0_1 >= x1_2 or  # No overlap along x-axis
                    y1_1 <= y0_2 or y0_1 >= y1_2 or  # No overlap along y-axis
                    z1_1 <= z0_2 or z0_1 >= z1_2)    # No overlap along z-axis


def fitness_function(ulds_list, packages_list):
    """Calculates the fitness score of a solution."""
    fitness_score = 0
    weight_penalty = 0
    stability_penalty = 0
    unplaced_packages_penalty = 0
    priority_spread_penalty = 0

    num_priority_uld = sum(1 for uld in ulds_list if any(pkg.priority for pkg in uld.packages))
    unplaced_economy_packages = sum(1 for pkg in packages_list if not pkg.placed and not pkg.priority)

    for uld in ulds_list:
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
    """Checks if a package is stably placed within a ULD."""
    for other_package in uld.packages:
        if package.position and other_package.position:
            if (package.position[2] > other_package.position[2] and 
                package.weight > other_package.weight):
                return False
    return True


def create_initial_population(ulds_list, packages_list, population_size):
    """Creates the initial population for the genetic algorithm."""
    population = []
    
    for _ in range(population_size):
        random.shuffle(packages_list)
        solution = []
        
        for uld in ulds_list:
            for package in packages_list:
                uld.add_package(package)  # Weight constraint is now respected.
                
            solution.append(uld)
        
        population.append(solution)
    
    return population


def generate_output(ulds_list, packages_list):
    """Generates the final output in the required format."""
    total_cost = -fitness_function(ulds_list, packages_list)
    total_packed = sum(1 for pkg in packages_list if pkg.placed)
    num_priority_uld = sum(1 for uld in ulds_list if any(pkg.priority for pkg in uld.packages))

    output_lines = [f"{total_cost},{total_packed},{num_priority_uld}"]
    
    for pkg in packages_list:
        if pkg.placed:
            x0, y0, z0, x1, y1, z1 = pkg.position
            output_lines.append(f"{pkg.id},{pkg.uld_id},{x0},{y0},{z0},{x1},{y1},{z1}")
        else:
            output_lines.append(f"{pkg.id},NONE,-1,-1,-1,-1,-1,-1")
    
    return "\n".join(output_lines)


if __name__ == "__main__":
    ulds_data_new_name = [
        ULD("U1", 224, 318, 162, 100),
        ULD("U2", 244, 318, 244, 70)
    ]
    
    packages_data_new_name = [
        Package("P-1", 50, 50, 50, 20, False, 100),
        Package("P-2", 70, 60, 60, 30, True, None),
        Package("P-3", 100, 100, 50, 50, False, 200),
        Package("P-4", 30, 30, 30, 10, True, None)
    ]
    
    best_solution_new_name = create_initial_population(ulds_data_new_name.copy(), packages_data_new_name.copy(), population_size=10)
    
    output_result_new_name = generate_output(ulds_data_new_name.copy(), packages_data_new_name.copy())
    
    print(output_result_new_name)
