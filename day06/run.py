from typing import List, Optional
from pydantic import BaseModel


class ParsedOrbit(BaseModel):
    parent: str
    child: str


def parse_line(line):
    parent, child = line.split(')')
    return ParsedOrbit(parent=parent, child=child)


def parse(input):
    return [
        parse_line(line) for line in input.split('\n')
        if line
    ]


class Body(BaseModel):
    orbited: List[str]
    parent: Optional[str]


def get_bodies(parsed_inputs):
    locations = {}
    for orbit in parsed_inputs:
        if orbit.parent not in locations:
            locations[orbit.parent] = Body(parent=None, orbited=[orbit.child])
        else:
            locations[orbit.parent].orbited.append(orbit.child)

        if orbit.child not in locations:
            locations[orbit.child] = Body(parent=orbit.parent, orbited=[])
        else:
            locations[orbit.child].parent = orbit.parent

    return locations


def calc_orbit(orbits, orbit_name, current_orbit):
    return current_orbit + sum([
        calc_orbit(orbits, x, current_orbit + 1)
        for x in orbits[orbit_name].orbited
    ])


def find_total_orbits(orbits):
    return calc_orbit(orbits, 'COM', 0)



with open('test_orbits.txt') as f:
    input_orbits = parse(f.read())


bodies = get_bodies(input_orbits)
assert find_total_orbits(bodies) == 42


with open('input.txt') as f:
    input_orbits = parse(f.read())
bodies = get_bodies(input_orbits)
print('Found orbits: %s' % find_total_orbits(bodies))


def find_orbit_path_to_centre(bodies, body):
    orbit_path = []
    while True:
        if not bodies[body].parent:
            return orbit_path

        body = bodies[body].parent
        orbit_path.append(body)


# def closet_join(path_1, path_2):
#     for body in path_1:
#         if body in path_2:
#             return body


def closet_join(path_1, path_2):
    previous = None
    
    for body1, body2 in zip(path_1[::-1], path_2[::-1]):
        if body1 != body2:
            return previous

        previous = body1


def find_orbit_path_length(bodies):
    path_Y = find_orbit_path_to_centre(bodies, "YOU")
    path_S = find_orbit_path_to_centre(bodies, "SAN")

    closest = closet_join(path_Y, path_S)

    index_Y = path_Y.index(closest)
    index_S = path_S.index(closest)

    return index_Y + index_S

with open('test_part2.txt') as f:
    input_orbits = parse(f.read())

# import pdb; pdb.set_trace()
bodies = get_bodies(input_orbits)

closest_you = find_orbit_path_to_centre(bodies, "YOU")
closest_san = find_orbit_path_to_centre(bodies, "SAN")
assert closest_you == ['K', 'J', 'E', 'D', 'C', 'B', 'COM']
assert closest_san == ['I', 'D', 'C', 'B', 'COM']
assert closet_join(closest_you, closest_san) == 'D'
assert find_orbit_path_length(bodies) == 4

with open('input.txt') as f:
    input_orbits = parse(f.read())
bodies = get_bodies(input_orbits)
print('Found orbits: %s' % find_orbit_path_length(bodies))
