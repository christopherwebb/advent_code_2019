# R75,D30,R83,U83,L12,D49,R71,U7,L72
# U62,R66,U55,R34,D71,R55,D58,R83 = distance 159
# R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51
# U98,R91,D20,R16,D67,R40,U7,R15,U6,R7 = distance 135

class WireVector:
    def __init__(self, direction, length):
        self.direction = direction
        self.length = length

    def get_journey(self, origin):
        if self.direction == 'U':
            return [(origin[0], origin[1] + x) for x in range(1, self.length + 1)]

        elif self.direction == 'R':
            return [(origin[0] + x, origin[1]) for x in range(1, self.length + 1)]

        elif self.direction == 'D':
            return [(origin[0], origin[1] - x) for x in range(1, self.length + 1)]

        elif self.direction == 'L':
            return [(origin[0] - x, origin[1]) for x in range(1, self.length + 1)]


def parse_routes(routes_str):
    routes_str.strip()
    return [parse_route(x) for x in routes_str.split('\n') if x]


def parse_route(route_str):
    route_str.strip()
    points = route_str.split(',')
    return [parse_vector(x.strip()) for x in points if x]


def parse_vector(vector_str):
    return WireVector(vector_str[0], int(vector_str[1:]))


def calculate_minimum_cross(route_1, route_2):
    results = get_crosses(route_1, route_2)
    return min(manhat_distance(x) for x in results)


def manhat_distance(point):
    return abs(point[0]) + abs(point[1])


def get_crosses(route_1, route_2):
    route_1_journey = get_journey(route_1)
    route_2_journey = get_journey(route_2)

    return set(route_1_journey) & set(route_2_journey) - set([(0,0)])


def get_journey(route):
    route_1_journey = [(0,0)]
    for vector in route:
        route_1_journey += vector.get_journey(route_1_journey[-1])
    return route_1_journey


def calculate_closest_cross(route_1, route_2):
    results = get_crosses(route_1, route_2)

    journey_1 = get_journey(route_1)
    journey_2 = get_journey(route_2)

    steps = []
    for result in results:
        length_1 = journey_1.index(result)
        length_2 = journey_2.index(result)
        steps.append(length_1 + length_2)

    return min(steps)



test_1_r1 = "R75,D30,R83,U83,L12,D49,R71,U7,L72"
test_1_r2 = "U62,R66,U55,R34,D71,R55,D58,R83"
test_2_r1 = "R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51"
test_2_r2 = "U98,R91,D20,R16,D67,R40,U7,R15,U6,R7"

assert WireVector('U', 2).get_journey((0,0)) == [(0,1), (0,2)]
assert WireVector('R', 4).get_journey((2,3)) == [(3,3), (4,3), (5,3), (6,3)]
assert WireVector('L', 3).get_journey((-2,2)) == [(-3,2), (-4,2), (-5,2)]
assert WireVector('D', 1).get_journey((0,7)) == [(0,6)]

assert len(parse_route(test_1_r1)) == 9
assert parse_route(test_1_r2)[-1].length == 83
assert parse_route(test_2_r1)[-2].direction == 'U'

assert calculate_minimum_cross(parse_route(test_1_r1), parse_route(test_1_r2)) == 159
assert calculate_minimum_cross(parse_route(test_2_r1), parse_route(test_2_r2)) == 135

with open('input.txt') as f:
    route_1, route2 = parse_routes(f.read())

result = calculate_minimum_cross(route_1, route2)
print('Minimum cross distance %s' % result)

assert calculate_closest_cross(parse_route(test_1_r1), parse_route(test_1_r2)) == 610
assert calculate_closest_cross(parse_route(test_2_r1), parse_route(test_2_r2)) == 410

result = calculate_closest_cross(route_1, route2)
print('Minimum steps distance %s' % result)
