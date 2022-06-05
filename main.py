from prettytable import PrettyTable
import math

stage_1_table = [
    #    P   x   y   z   s1  s2  s3  RHS
    [1, -6, -5, -3,  0,  0,  0,   0],
    [0,  7,  7,  4,  1,  0,  0,  23],
    [0,  5,  6,  2,  0,  1,  0,  16],
    [0,  4,  8, -2,  0,  0,  1,  13],
]

stage_2_table = [
    # Q  P   x   y   z   s1  s2  s3  s4  a1  a2  RHS
    [1,  0,  2,  0,  2,  0,  0, -1, -1,  0,  0,  19],
    [0,  1, -2, -3, -1,  0,  0,  0,  0,  0,  0,   0],
    [0,  0,  1,  1,  1,  1,  0,  0,  0,  0,  0,  20],
    [0,  0,  0,  2,  1,  0,  1,  0,  0,  0,  0,  22],
    [0,  0,  0,  0,  1,  0,  0, -1,  0,  1,  0,   4],
    [0,  0,  2,  0,  1,  0,  0,  0, -1,  0,  1,  15],
]


def print_table(table, feild_names):
    pretty_table = PrettyTable()
    pretty_table.field_names = feild_names
    for row in table:
        pretty_table.add_row([round(i, 2) for i in row])
    print(pretty_table)


def find_pivotal_column_one_stage(table):
    '''
    Finds the variable with the most negative value 
    in the objective function row
    '''
    lowest_index = -1
    lowest_value = math.inf
    for i in range(len(table[0])):
        if table[0][i] < lowest_value:
            lowest_index = i
            lowest_value = table[0][i]
    return lowest_index


def find_pivotal_column_two_stage(table, num_variables=3):
    '''
    Finds the variable with the most positive value 
    in the objective function row
    '''
    highest_index = -1
    highest_value = -math.inf
    for i in range(2, 2 + num_variables):
        if table[0][i] > highest_value:
            highest_index = i
            highest_value = table[0][i]
    return highest_index


def find_pivotal_row_one_stage(table, pivotal_column):
    '''
    Compares RHS / pivotal column for each row 
    and chooses the smallest non negative value
    '''
    smallest_index = -1
    smallest_value = math.inf

    for i in range(1, len(table)):
        if table[i][pivotal_column] != 0 and 0 <= (temp := table[i][-1] / table[i][pivotal_column]) < smallest_value:
            smallest_index = i
            smallest_value = temp
    return smallest_index


def find_pivotal_row_two_stage(table, pivotal_column):
    '''
    Compares RHS / pivotal column for each row 
    and chooses the smallest non negative value
    '''
    smallest_index = -1
    smallest_value = math.inf

    for i in range(2, len(table)):
        if table[i][pivotal_column] != 0 and 0 <= (temp := table[i][-1] / table[i][pivotal_column]) < smallest_value:
            smallest_index = i
            smallest_value = temp
    return smallest_index


def normalise_pivot(table, pivotal_column, pivotal_row):
    '''
    Divides pivotal row by value in pivotal column
    '''
    table[pivotal_row] = [i / table[pivotal_row][pivotal_column]
                          for i in table[pivotal_row]]


def make_pivotal_column_zero(table, pivotal_column, pivotal_row):
    '''
    Subtracts multiples of the pivotal row to all other rows 
    to make them equal zero in the pivotal column
    '''
    for row in range(len(table)):
        if row != pivotal_row:
            table[row] = [table[row][i] - table[row][pivotal_column] *
                          table[pivotal_row][i] for i in range(len(table[row]))]


def check_if_optimal(table):
    '''
    Checks if an optimal solution has been found by checking
    if there are any negatives in the objective function row
    '''
    for i in table[0]:
        if i < 0:
            return False
    return True


def check_if_feasible(table, num_variables=3):
    '''
    Checks if in feasable region by checking if all variables are <= 0
    '''
    for i in table[0][2: 2 + num_variables]:
        if i > 0:
            return False
    return True


def interpret_values(table, feilds):
    values = [table[0][-1]]
    for col in range(1, len(table[0]) - 1):
        if table[0][col] != 0:
            values.append(0)
        else:
            for row in range(len(table)):
                if table[row][col] == 1:
                    values.append(table[row][-1])

    pretty_table = PrettyTable()
    pretty_table.field_names = ['Variable', 'Value']
    for value, feild in zip(values, feilds):
        pretty_table.add_row([feild, round(value, 2)])
    print(pretty_table)


def make_stage_one_table(table, num_variables, num_slack):
    '''
    Converts a feasible stage two table to a stage one table
    '''
    new_table = []
    for row in range(1, len(table)):
        new_table.append(table[row][1:2 + (num_variables +
                                           num_slack)] + table[row][-1:])
    return new_table


def make_feilds(is_two_stage, num_variables, num_slack, num_artifcial=0):
    feilds = []
    if is_two_stage:
        feilds.append('Q')
    feilds.append('P')
    for i in range(num_variables):
        feilds.append(['x', 'y', 'z'][i])
    for i in range(num_slack):
        feilds.append(f's{i + 1}')
    for i in range(num_artifcial):
        feilds.append(f'a{i + 1}')
    feilds.append("RHS")
    return feilds


def solve_one_stage(table, num_variables, num_slack, stage=1, feilds=None):
    if feilds == None:
        feilds = make_feilds(False, num_variables, num_slack)
    print(f'\nTableau {stage}:')
    print_table(table, feilds)

    pivotal_column = find_pivotal_column_one_stage(table)
    pivotal_row = find_pivotal_row_one_stage(table, pivotal_column)

    normalise_pivot(table, pivotal_column, pivotal_row)
    make_pivotal_column_zero(table, pivotal_column, pivotal_row)

    if not check_if_optimal(table):
        solve_one_stage(table, num_variables, num_slack, stage + 1, feilds)
    else:
        print(f'\nTableau {stage + 1}:')
        print_table(table, feilds)
        print(f'\nSolutions: ')
        interpret_values(table, feilds)


def solve_two_stage(table, num_variables, num_slack, num_artefical, stage=1, feilds=None):
    if feilds == None:
        feilds = make_feilds(True, num_variables, num_slack, num_artefical)
    print(f'\nTableau {stage}:')
    print_table(table, feilds)

    pivotal_column = find_pivotal_column_two_stage(table)
    pivotal_row = find_pivotal_row_two_stage(table, pivotal_column)

    normalise_pivot(table, pivotal_column, pivotal_row)
    make_pivotal_column_zero(table, pivotal_column, pivotal_row)

    if not check_if_feasible(table):
        solve_two_stage(table, num_variables, num_slack,
                        num_artefical, stage + 1)
    else:
        table = make_stage_one_table(table, num_variables, num_slack)
        solve_one_stage(table, num_variables, num_slack, stage + 1)


solve_two_stage(stage_2_table, 3, 4, 2)
