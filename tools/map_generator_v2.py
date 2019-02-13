#!/usr/bin/python

import math
import random

# minimum and maximum total number of planets in map
minPlanets = 15
maxPlanets = 30
# maximum number of planets specifically generated to be equidistant from both
# players, by chance planet generated in the standard symmetric way could still
# end up equidistant as well
# also does not include the planet exactly in the center of the map
maxCentral = 5
# minimum and maximum number of ships on neutral planets
minShips = 1
maxShips = 100
# minimum and maximum growth for planets
# except for the center planet which is always 0 minimum growth
minGrowth = 1
maxGrowth = 5
# minimum distance between planets
minDistance = 2
# minimum distance between the players starting planets
minStartingDistance = 4
# maximum radius from center of map a planet can be
maxRadius = 15
# minimum difference between true distance and rounded distance between planets
# this is to try and avoid rounding errors causing different distances to be
# calculated on different platforms and languages
epsilon = 0.002


def make_planet(x, y, owner, num_ships, growth_rate):
    return {"x": x, "y": y, "owner": owner, "num_ships": num_ships,
            "growth_rate": growth_rate}


def print_planet(p):
    out = ["P", p["x"], p["y"], p["owner"], p["num_ships"], p["growth_rate"]]
    return " ".join(str(i) for i in out)


def translate_planets(planets):
    for p in planets:
        p["x"] += maxRadius
        p["y"] += maxRadius


def generate_coordinates(p, r, theta):
    if theta < 0:
        theta += 360
    if theta >= 360:
        theta -= 360
    p["x"] = r * math.cos(math.radians(theta))
    p["y"] = r * math.sin(math.radians(theta))


def rand_num(minimum, maximum):
    return (random.random() * (maximum - minimum)) + minimum


def rand_radius(min_r, max_r):
    val = min_r - 1
    while val < min_r:
        val = math.sqrt(random.random()) * max_r
    return val


def distance(p1, p2):
    return math.ceil(actual_distance(p1, p2))


def actual_distance(p1, p2):
    dx = p1["x"] - p2["x"]
    dy = p1["y"] - p2["y"]
    return math.sqrt(dx * dx + dy * dy)


def not_valid(p1, p2, planets):
    a_distance = actual_distance(p1, p2)
    if distance(p1, p2) < minDistance or abs(a_distance - round(a_distance)) < epsilon:
        return True
    for p in planets:
        a_distance1 = actual_distance(p, p1)
        a_distance2 = actual_distance(p, p2)
        if (distance(p, p1) < minDistance
                or distance(p, p2) < minDistance
                or abs(a_distance1 - round(a_distance1)) < epsilon
                or abs(a_distance2 - round(a_distance2)) < epsilon):
            return True
    return False


def not_valids(p1, planets):
    for p in planets:
        a_distance = actual_distance(p, p1)
        if distance(p, p1) < minDistance or abs(a_distance - round(a_distance)) < epsilon:
            return True
    return False


def generate_map():
    # works out information about the map
    planets_to_generate = random.randint(minPlanets, maxPlanets)
    if random.randint(0, 1):
        symmetry_type = 1  # radial symmetry
        # can only generate an odd number of planets in this symmetry
        while planets_to_generate % 2 == 0:
            if planets_to_generate == maxPlanets:
                planets_to_generate = minPlanets
            else:
                planets_to_generate += 1
    else:
        symmetry_type = -1  # linear symmetry

    planets = [make_planet(0, 0, 0, random.randint(minShips, maxShips),
                           random.randint(0, maxGrowth))]

    # adds the centre planet
    planets_to_generate -= 1

    # picks out the home planets
    r = rand_radius(minDistance, maxRadius)
    theta1 = rand_num(0, 360)
    if symmetry_type == 1 and theta1 < 180:
        theta2 = theta1 + 180
    elif symmetry_type == 1:
        theta2 = theta1 - 180
    else:
        theta2 = rand_num(0, 360)

    p1 = make_planet(0, 0, 1, 100, 5)
    p2 = make_planet(0, 0, 2, 100, 5)
    generate_coordinates(p1, r, theta1)
    generate_coordinates(p2, r, theta2)

    while not_valid(p1, p2, planets) or distance(p1, p2) < minStartingDistance:
        r = rand_radius(minDistance, maxRadius)
        theta1 = rand_num(0, 360)
        if symmetry_type == 1 and theta1 < 180:
            theta2 = theta1 + 180
        elif symmetry_type == 1:
            theta2 = theta1 - 180
        else:
            theta2 = rand_num(0, 360)

        generate_coordinates(p1, r, theta1)
        generate_coordinates(p2, r, theta2)
    planets.append(p1)
    planets.append(p2)
    planets_to_generate -= 2

    # makes the center neutral planets
    if symmetry_type == 1:
        no_center_neutrals = 2 * random.randint(0, maxCentral // 2)
        theta_a = (theta1 + theta2) / 2
        theta_b = theta_a + 180
        for i in range(no_center_neutrals // 2):
            r = rand_radius(minDistance, maxRadius)
            num_ships = random.randint(minShips, maxShips)
            growth_rate = random.randint(minGrowth, maxGrowth)
            p1 = make_planet(0, 0, 0, num_ships, growth_rate)
            p2 = make_planet(0, 0, 0, num_ships, growth_rate)
            generate_coordinates(p1, r, theta_a)
            generate_coordinates(p2, r, theta_b)
            while not_valid(p1, p2, planets):
                r = rand_radius(minDistance, maxRadius)
                generate_coordinates(p1, r, theta_a)
                generate_coordinates(p2, r, theta_b)
            planets.append(p1)
            planets.append(p2)
            planets_to_generate -= 2
    else:
        # must have an even number of planets left to generate after this
        min_central = planets_to_generate % 2
        no_center_neutrals = random.randrange(min_central, maxCentral + 1, 2)
        theta = (theta1 + theta2) / 2
        if random.randint(0, 1) == 1:
            theta += 180
        for i in range(no_center_neutrals):
            r = rand_radius(0, maxRadius)
            num_ships = random.randint(minShips, maxShips)
            growth_rate = random.randint(minGrowth, maxGrowth)
            p = make_planet(0, 0, 0, num_ships, growth_rate)
            generate_coordinates(p, r, theta)
            while not_valids(p, planets):
                r = rand_radius(0, maxRadius)
                generate_coordinates(p, r, theta)
            planets.append(p)
            planets_to_generate -= 1

    # picks out the rest of the neutral planets
    assert planets_to_generate % 2 == 0, "Error: odd number of planets left to add"
    for i in range(planets_to_generate // 2):
        r = rand_radius(minDistance, maxRadius)
        theta = rand_num(0, 360)
        if i == 0:
            planet_max = min(100, 5 * distance(planets[1], planets[2]) - 1)
            num_ships = random.randint(minShips, planet_max)
        else:
            num_ships = random.randint(minShips, maxShips)
        growth_rate = random.randint(minGrowth, maxGrowth)
        p1 = make_planet(0, 0, 0, num_ships, growth_rate)
        p2 = make_planet(0, 0, 0, num_ships, growth_rate)
        generate_coordinates(p1, r, theta1 + theta)
        generate_coordinates(p2, r, theta2 + symmetry_type * theta)

        while not_valid(p1, p2, planets):
            r = rand_radius(minDistance, maxRadius)
            theta = rand_num(0, 360)
            generate_coordinates(p1, r, theta1 + theta)
            generate_coordinates(p2, r, theta2 + symmetry_type * theta)
        planets.append(p1)
        planets.append(p2)

    translate_planets(planets)

    return "\n".join(map(print_planet, planets))


def save_map(f="generated.txt"):
    file_object = open(f, "w+")
    file_object.write(generate_map())
    file_object.close()


if __name__ == "__main__":
    print(generate_map())
