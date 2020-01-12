# Fuel required to launch a given module is based on its mass. 
# Specifically, to find the fuel required for a module, take its mass,
# divide by three, round down, and subtract 2.
def calc_fuel(mass):
    return int(mass / 3) - 2

test_data = [
    [12, 2],
    [14, 2],
    [1969, 654],
    [100756, 33583],
]

for test in test_data:
    assert calc_fuel(test[0]) == test[1]

def load_lines(path):
    with open(path) as f:
        data = f.read()

    return [x for x in data.split('\n') if x]

def process_input(path):
    raw_input = load_lines(path)
    return [int(x) for x in raw_input]


inputs = process_input('input_1.txt')
result = sum(calc_fuel(x) for x in inputs)

print('Fuel req: %s' % result)

# * A module of mass 14 requires 2 fuel. This fuel requires no further fuel (2
#   divided by 3 and rounded down is 0, which would call for a negative fuel),
#   so the total fuel required is still just 2.
# * At first, a module of mass 1969 requires 654 fuel. Then, this fuel requires
#   216 more fuel (654 / 3 - 2). 216 then requires 70 more fuel, which requires 21
#   fuel, which requires 5 fuel, which requires no further fuel. So, the total
#   fuel required for a module of mass 1969 is 654 + 216 + 70 + 21 + 5 = 966.
# * The fuel required by a module of mass 100756 and its fuel is:
#   33583 + 11192 + 3728 + 1240 + 411 + 135 + 43 + 12 + 2 = 50346.

test_data_2 = [
    [14, 2],
    [1969, 966],
    [100756, 50346]
]

def calc_fuel_2(mass):
    if mass <= 0:
        return 0

    res = calc_fuel(mass)
    extra = calc_fuel_2(res)

    return max(0, res + extra)

assert calc_fuel_2(14) == 2
assert calc_fuel_2(1969) == 966 
assert calc_fuel_2(100756) == 50346

result = sum(calc_fuel_2(x) for x in inputs)
print('Fuel req 2: %s' % result)
