# Other than the range rule, the following are true:

# 111111 meets these criteria (double 11, never decreases).
# 223450 does not meet these criteria (decreasing pair of digits 50).
# 123789 does not meet these criteria (no double).
# How many different passwords within the range given in your puzzle input meet these criteria?

# Your puzzle input is 178416-676461.

def matches(selection):
    groups = []
    growing = True
    for selec in selection:
        if groups and selec < groups[-1][0]:
            return False

        if groups and groups[-1][0] == selec:
            groups[-1].append(selec)
        else:
            groups.append([selec])

    return bool([x for x in groups if len(x) >= 2])

def matches2(selection):
    groups = []
    for selec in selection:
        if groups and selec < groups[-1][0]:
            return False

        if groups and groups[-1][0] == selec:
            groups[-1].append(selec)
        else:
            groups.append([selec])

    return bool([x for x in groups if len(x) == 2])

def parse(input):
    return [int(i) for i in input]

def find_matches(range_from, range_to, operation):
    return [
        x for x in range(range_from, range_to + 1)
        if operation(parse(str(x)))
    ]

assert parse('111111') == [1, 1, 1, 1, 1, 1]
assert parse('223450') == [2, 2, 3, 4, 5, 0]
assert parse('123789') == [1, 2, 3, 7, 8, 9]
assert matches(parse('111111'))
assert not matches(parse('223450'))
assert not matches(parse('123789'))

print('Found: %s' % len(find_matches(178416, 676461, matches)))

assert matches2(parse('112233'))
assert not matches2(parse('123444'))
assert matches2(parse('111122'))

print('Found 2: %s' % len(find_matches(178416, 676461, matches2)))
