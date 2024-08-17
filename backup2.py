from time import time
import sys

FRONT_ROWS = 1
TIMEOUT = 1000
PARTNER_LIMIT = 2

# weight of each list when organizing
COMP_R_POINTS = 2
INCOMP_R_POINTS = 1
FRONTS_R_POINTS = 4

removed = []
names = []
positions = []
assignments = {}
tally = {}
timeout = True

# compatibles, incompatibles, fronts
c = []
i = []
f = []

# class dimensions
width = 6
height = 5

def main():

    find_possible_positions()
    load_names()
    start_tally()
    verify_dimensions()
    fetch_preferences()
    sort_names()

    start_time = time()
    while timeout:
        assignments.clear()
        start_tally()
        timer = time()
        if find_solution(0, timer):
            if timeout:
                removed.append(neglect_problematic_preference())
        else:
            print("Impossible request.\nNeglecting most problematic user preference.")
            removed.append(neglect_problematic_preference())

    print_class()
    print(f"Compatibles: {len(c)}")
    print(f"Incompatibles {len(i)}")
    print(f"Fronts: {len(f)}")
    print(f"Removed: {len(removed)}")
    print(f"Total time: {time() - start_time}s")
    print()
    print(f"Compatibles: {c}")
    print(f"Incompatibles {i}")
    print(f"Fronts: {f}")
    print(f"Removed: {removed}")

def verify_dimensions():
    if len(names) > height * width:
        print("Class too small for this many students.")
        sys.exit(1)


def find_solution(n, timer):

    global timeout

    # Positioned every student; return True.
    if n == len(names):
        timeout = False
        return True
    
    # "Travel" down the tree of possibilities. Cut branches that don't work.
    all_possible = identify_possible_positions(names[n])
    for position in all_possible:
        if is_possible(names[n], position):
            assignments[names[n]] = position
            if not find_solution(n+1, timer):
                del assignments[names[n]]
                if (time() - timer) > TIMEOUT:
                    print("Timeout")
                    return True
            else:
                return True
        else:
            tally[names[n]] += 1
    return False

def identify_possible_positions(student):

    # find unassigned positions
    possible_positions = []
    for pos in positions:
        if pos not in assignments.values():
            possible_positions.append(pos)

    # student must be near his compatible partners
    restricted_to = []
    comp_partners = c_partners(student)
    for s in comp_partners:
        if s in assignments:
            adjacent_x = get_adjacent_positions_x(assignments[s])
            for pos in adjacent_x:    
                restricted_to.append(pos)
    if restricted_to:
        to_remove = []
        for pos in possible_positions:
            if pos not in restricted_to:
                to_remove.append(pos)
        for pos in to_remove:
            possible_positions.remove(pos)
    
    # student must be "far" from his incompatible partners
    to_remove = []
    incomp_partners = i_partners(student)
    for pos in possible_positions:
        for s in incomp_partners:
            if s in assignments:
                if are_within_3x3(pos, assignments[s]):
                    to_remove.append(pos)
    for pos in to_remove:
        possible_positions.remove(pos)

    # student must need to be restricted to front of class
    to_remove = []
    if student in f:
        for pos in possible_positions:
            if pos[1] >= FRONT_ROWS:
                to_remove.append(pos)
        for pos in to_remove:
            possible_positions.remove(pos)
    
    return possible_positions


def is_possible(student, position):
    global c, i, f
    for n1, lst in enumerate([c,i]):
        for pair in lst:
            for n2 in range(2):
                if student == pair[n2%2] and pair[(n2+1)%2] in assignments:
                    # Compatibles too far
                    if n1 == 0 and (not are_adjacent_x(position, assignments[pair[(n2+1)%2]])):
                        return False
                    # Incompatibles too close
                    elif n1 == 1 and are_within_3x3(position, assignments[pair[(n2+1)%2]]):
                        return False
    # Front student too far back
    if student in f and position[1] >= FRONT_ROWS:
        return False
    
    # student is "trapped"
    if is_trapped_x(student, position):
        return False
    
    # x-neighbooring students are "trapped"
    adj_positions = get_adjacent_positions_x(position)
    for pos in adj_positions:
        if pos in assignments.values():
            name = get_key(pos, assignments)
            if is_trapped_x(name, pos):
                return False
            
    return True

# returns true if a student with compatible partners is surrounded by non-compatible students
def is_trapped_x(student, position):
    partners = c_partners(student)
    if (count := len(partners)) == 0:
        return False
    adjacent_positions = get_adjacent_positions_x(position)
    for pos in adjacent_positions:
        if pos in assignments.values():
            name = get_key(pos, assignments)
            if name in partners:
                count -= 1
        else:
            count -= 1
    if count > 0:
        return True
    return False


# returns all students who are compatible with input
def c_partners(student):
    partners = []
    for pair in c:
        for n3 in range(2):
            if pair[n3%2] == student:
                partners.append(pair[(n3+1)%2])
    return partners

# returns all students who are incompatible with input
def i_partners(student):
    partners = []
    for pair in i:
        for n3 in range(2):
            if pair[n3%2] == student:
                partners.append(pair[(n3+1)%2])
    return partners

def get_adjacent_positions(position):
    positions = [(position[0] + 1, position[1]), (position[0], position[1] + 1), 
                 (position[0] - 1, position[1]), (position[0], position[1] - 1)]
    to_remove = []
    for pos in positions:
        if pos[0] < 0 or pos[0] >= width or pos[1] < 0 or pos[1] >= height:
            to_remove.append(pos)
    for pos in to_remove:
        positions.remove(pos)
    return positions

def get_adjacent_positions_x(position):
    positions = [(position[0] + 1, position[1]), (position[0] - 1, position[1])]
    to_remove = []
    for pos in positions:
        if pos[0] < 0 or pos[0] >= width:
            to_remove.append(pos)
    for pos in to_remove:
        positions.remove(pos)
    return positions


def are_adjacent(position, partner_position):
    for n in range(2):
        if (int(abs(position[1] - partner_position[1])) <= int(n%2) and
            int(abs(position[0] - partner_position[0])) <= int((n+1)%2)):
            return True
    return False

def are_adjacent_x(position, partner_position):
    if (int(abs(position[1] - partner_position[1])) == 0 and
        int(abs(position[0] - partner_position[0])) == 1):
        return True
    return False

def are_within_3x3(position, partner_position):
    if (int(abs(position[1] - partner_position[1])) <= 1 and
        int(abs(position[0] - partner_position[0])) <= 1):
        return True
    return False

def neglect_problematic_preference():
    global c, i, f
    # find student who cut the most branches
    max = 0
    blamed = next(iter(tally))
    for s in tally:
        if tally[s] > max:
            max = tally[s]
            blamed = s
    # compatibles are most likely to cause problems
    for pair in c:
        if blamed in pair:
            c.remove(pair)
            return ("C", pair)
    # fronts
    for stdnt in f:
        if s == blamed:
            f.remove(s)
            return ("F", stdnt)
    # incompatibles
    for pair in i:
        if blamed in pair:
            i.remove(pair)
            return ("I", pair)

def sort_names():
    global names
    # more restricted seating goes first
    # every name is alloted points based on how "restricted" they are
    restriction_levels = {}
    for name in names:
        restriction_levels[name] = 0
    for pair in c:
        for s in pair:
            restriction_levels[s] += COMP_R_POINTS
    for pair in i:
        for s in pair:
            restriction_levels[s] += INCOMP_R_POINTS
    for s in f:
            restriction_levels[s] += FRONTS_R_POINTS
    restriction_levels_sorted = dict(sorted(restriction_levels.items(), key=lambda item: item[1], reverse=True))
    names_s = []
    for count in restriction_levels_sorted:
        names_s.append(count[0])
    names = names_s

def get_key(value, dictionary):
    for key in dictionary:
        if dictionary[key] == value:
            return key
    print("get_key() fnction failed; no key.")
    sys.exit(2)


def find_possible_positions():
    global positions
    for x in range(width):
        for y in range(height):
            positions.append((x,y))

def load_names():
    with open("input.txt", "r") as input:
        for line in input:
            names.append(line.strip())

def start_tally():
    for name in names:
        tally[name] = 0

# Retrieves lists of compatibles, incomptibles, fronts
def fetch_preferences():
    global c, i, f
    for n, lst in enumerate([c,i]):
        print("Compatibles" if n == 0 else "Incompatibles")
        while (s1 := input("S1: ")) != '' and (s2 := input("S2: ")) != '':
            pair = (s1,s2)
            if (pair[0] not in names or pair[1] not in names):
                print("Student not in class.")
            elif pair[0] == pair[1]:
                print("Pair must contain two DIFFERENT students.")
            elif (((pair in c or ((pair[1],pair[0])) in c) and lst == i)
                   or ((pair in i or (pair[1],pair[0]) in i)and lst == c)):
                print("Students cannot be both compatible and incompatible.")
            elif (pair in lst or (pair[1],pair[0]) in lst):
                print("Already in list.")
            elif ((len(c_partners(pair[0])) >= PARTNER_LIMIT or len(c_partners(pair[1])) >= PARTNER_LIMIT)
                   and (lst == c)):
                print(f"Max of {PARTNER_LIMIT} compatible parters per student.")
            else:
                lst.append(pair)
    print("Fronts")
    while (s := input("S: ")) != '':
        if s in names:
            f.append(s) if len(f) < FRONT_ROWS * width else print("Front limit reached.")
        else:
            print("Student not in class")

def print_class():
    # sort assignments
    with open("output.txt", "w") as output:
        for y in range(height):
            for x in range(width):
                found = False
                for s in assignments:
                    if assignments[s] == (x, y):
                        output.write(f"{s} ")
                        found = True
                        break
                if not found:
                    output.write("# ")
            output.write("\n")

main()