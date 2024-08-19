from time import time
from math import floor
import sys

FRONT_ROWS = 1
RELEGATED_FRONT_ROWS = 2
TIMEOUT = 10
PARTNER_LIMIT = 4

# weight of each list when organizing
COMP_R_POINTS = 2
INCOMP_R_POINTS = 1
FRONTS_R_POINTS = 3

removed = []
names = []
positions = set()
assignments = {}
tally = {}
timeout = True

# compatibles, incompatibles, fronts
c = []
i = []
f = []

# relegated compatibles, fronts
rc = []
rf = []

# class dimensions
width = 6
height = 4

def main():

    # prepare
    find_possible_positions()
    load_names()
    verify_dimensions()
    fetch_preferences()
    sort_names()
    address_comp_strings(width)

    # find solution
    start_time = time()
    while True:
        assignments.clear()
        tally.clear()
        timer = time()
        if not find_solution(0, timer):
            print("Impossible request.\nNeglecting most problematic user preference.")
            neglect_problematic_preference()
        elif timeout:
            print("Timeout")
            neglect_problematic_preference()
        else:
            break

    # print solution
    print_class()
    print_summary(start_time)

def verify_dimensions():
    if len(names) > height * width:
        print("Class too small for this many students.")
        sys.exit(1)


def find_solution(n, timer):

    global timeout

    # Solved layout, ie: positioned every student; return True.
    if n == len(names):
        timeout = False
        return True
    
    # find all possible positions for this student
    all_possible = identify_possible_positions(names[n])

    # "Travel" down the tree of possibilities. Cut branches that don't work.
    for position in all_possible:
        assignments[names[n]] = position
        if not find_solution(n+1, timer):
            del assignments[names[n]]
            if (time() - timer) > TIMEOUT:
                return True
        else:
            return True
    return False

def identify_possible_positions(student):

    # find unassigned positions
    possible_positions = set()
    for pos in positions:
        if pos not in assignments.values():
            possible_positions.add(pos)

    # student must be near his compatible partners
    restricted_to = set()
    comp_partners = c_partners(student)
    for s in comp_partners:
        if s in assignments:
            adjacent_x = get_adjacent_positions_x(assignments[s])
            restricted_to |= adjacent_x
    rcomp_partners = rc_partners(student)
    for s in rcomp_partners:
        if s in assignments:
            adjacent = get_adjacent_positions(assignments[s])
            restricted_to |= adjacent
    if restricted_to:
        possible_positions = possible_positions & restricted_to

    to_remove = set()
    incomp_partners = i_partners(student)
    for pos in possible_positions:

        # student must be "far" from his incompatible partners
        for s in incomp_partners:
            if s in assignments:
                if are_within_3x3(pos, assignments[s]):
                    to_remove.add(pos)
                    blame(student, "I")

        # " may need to be restricted to front of class
        if student in f and pos[1] >= FRONT_ROWS:
            to_remove.add(pos)
            blame(student, "F")
        elif student in rf and pos[1] >= RELEGATED_FRONT_ROWS:
            to_remove.add(pos)
            blame(student, "RF")

        # check if this position is "adjacent to" all currently assigned compatible partners
        for partner in comp_partners:
                if partner in assignments:
                    if not are_adjacent_x(pos, assignments[partner]):
                        to_remove.add(pos)
                        blame(student, "C")

        ## Trap checks ##
        # check if student is blocked from his compatible partners
        if is_trapped_x(student, pos):
            to_remove.add(pos)
            blame(student, "C")

        # check if his neighboors WOULD BE blocked from THEIR compatible partners
        adjacent_positions_x = get_adjacent_positions_x(pos)
        assignments[student] = pos
        for p in adjacent_positions_x:
            if p in assignments.values():
                name = get_key(p, assignments)
                if is_trapped_x(name, p) and pos not in to_remove:
                    to_remove.add(pos)
                    blame(student, "C")
        del assignments[student]

        # same as above, but less "restrictive". This uses the "relegated compatibles" list which allows
        # for partners to be positioned above/below the student rather than just beside the student.
        if is_trapped(student, pos) and pos not in to_remove:
            to_remove.add(pos)
            blame(student, "RC")

        adjacent_positions = get_adjacent_positions(pos)
        assignments[student] = pos
        for p in adjacent_positions:
            if p in assignments.values():
                name = get_key(p, assignments)
                if is_trapped(name, p) and pos not in to_remove:
                    to_remove.add(pos)
                    blame(student, "RC")
        del assignments[student]

        # number of f students cannot exceed number of frontbound positions
        available_f_positions = 0
        unassigned_f_students = len(f)
        for x in range(width):
            for y in range(FRONT_ROWS):
                if (x,y) not in assignments.values():
                    available_f_positions += 1
                elif get_key((x,y), assignments) in f:
                    unassigned_f_students -= 1
        if unassigned_f_students >= available_f_positions and pos[1] < FRONT_ROWS and student not in f:
            to_remove.add(pos)
            # add blame ?
            
    possible_positions -= to_remove
    
    return possible_positions

# eliminates comp strings of inputted length or longer
## a comp string is a set of compatible pairs that form a "string" which can be difficult or impossible to position
def address_comp_strings(length):
    while True:
        restart = False
        for pair in c:
            for s in pair:
                max_length = width * height + 1
                # start at max length, and iterate down until string found
                for i in range(max_length):
                    if max_length - i < length - 1:
                        break
                    if string := find_string(s, None, 0, s, max_length - i):
                        break
                if string:
                    print(f"Comp string or loop: {string}")
                    sever_comp_string(string)
                    restart = True
                    break
            if restart:
                break
        if not restart:
            break

# cuts string once found
def sever_comp_string(string):
    global c
    s1 = string[floor(len(string) / 2) - 1]
    s2 = string[floor(len(string) / 2)]
    for pair in [(s1,s2),(s2,s1)]:
        if pair in c:
            c.remove(pair)
            removed.append(pair)
            print(f"Removed: {pair}\n")
            break


# Identifies string of given length, else returns None
def find_string(current, previous, n, start, length):

    if n == length:
        return [current]
    
    # loop found
    if n > 0 and current == start:
        print("loop detected")
        return [current]
    
    partners = c_partners(current)
    if previous:
        partners.remove(previous)

    for next in partners:
        string = find_string(next, current, n + 1, start, length)
        if string:
            return [current] + string
    return None

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

# same as "is_trapped_x", but checks all adjacent positions -- not just left and right
# this also assumes that the student is part of the "relegated compatibles list"
def is_trapped(student, position):
    partners = rc_partners(student)
    if (count := len(partners)) == 0:
        return False
    adjacent_positions = get_adjacent_positions(position)
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

def rc_partners(student):
    partners = []
    for pair in rc:
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
    positions = {(position[0] + 1, position[1]), (position[0], position[1] + 1), 
                 (position[0] - 1, position[1]), (position[0], position[1] - 1)}
    to_remove = set( )
    for pos in positions:
        if pos[0] < 0 or pos[0] >= width or pos[1] < 0 or pos[1] >= height:
            to_remove.add(pos)
    for pos in to_remove:
        positions.remove(pos)
    return positions

def get_adjacent_positions_x(position):
    positions = {(position[0] + 1, position[1]), (position[0] - 1, position[1])}
    to_remove = set()
    for pos in positions:
        if pos[0] < 0 or pos[0] >= width:
            to_remove.add(pos)
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
    global c, i, f, rc, rf
    # find student who cut the most branches
    max = 0
    blamed = next(iter(tally))
    for s in tally:
        if tally[s] > max:
            max = tally[s]
            blamed = s

    # relegate
    if blamed[1] == "C":
        for pair in c:
            if blamed[0] in pair:
                relegate(pair)

    elif blamed[1] == "F":
        relegate(blamed[0])
    
    # remove
    elif blamed[1] == "I":
        for pair in i:
            if blamed[0] in pair:
                i.remove(pair)
                removed.append(("I",pair))
            
    elif blamed[1] == "RC":
        for pair in rc:
            if blamed[0] in pair:
                rc.remove(pair)
                removed.append(("RC",pair))

    elif blamed[1] == "RF":
        rf.remove(blamed[0])
        removed.append(("RF",blamed[0]))

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

# adds this student to the tally along with which list -- c, i, or f -- caused to problem
# the most "problematic" student is neglected

def blame(student, lst):
    try:
        tally[(student, lst)] += 1
    except KeyError:
        tally[(student, lst)] = 0

def get_key(value, dictionary):
    for key in dictionary:
        if dictionary[key] == value:
            return key
    print("get_key() fnction failed; no key.")
    sys.exit(2)

# moves student from main list to secondary list with less restrictions
def relegate(pair_or_student):
    global c, f, rc, rf
    for lst in [[c, rc], [f, rf]]:
        if pair_or_student in lst[0]:
            lst[0].remove(pair_or_student)
            lst[1].append(pair_or_student)


def find_possible_positions():
    global positions
    for x in range(width):
        for y in range(height):
            positions.add((x,y))

def load_names():
    with open("input.txt", "r") as input:
        for line in input:
            names.append(line.strip())

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
        if s in f:
            print("Already in list.")
        elif s in names:
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

def print_summary(start_time):
    print(f"""
Compatibles: {c}
Incompatibles: {i}
Fronts: {f}
Relegated Compatibles: {rc}
Relegated Fronts: {rf}
Removed: {removed}

{len(c)} Compatibles
{len(i)} Incompatibles
{len(f)} Fronts
{len(rc)} Relegated Compatibles
{len(rf)} Relegated Fronts
{len(removed)} Removed
Total time: {time() - start_time}
""")
    
main()