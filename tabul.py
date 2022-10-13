"""generate an ascii table"""

def tabulate(*args):
    """generate ascii table
    takes as many 2D arrays as you want
    each 2D array will be put into a table with out horizontal seperation
    horizontal seperation will be put between 2D arrays"""
    width = len(args[0][0])
    col_widths = []

    table = []
    for thing in args:
        table += thing

    for column in range(width):
        max_width = 0
        for row in table:
            if len(str(row[column])) > max_width:
                max_width = len(str(row[column]))
        col_widths.append(max_width)


    text = "┌"
    for i in range(width):
        text += "─" * col_widths[i]
        if i != width - 1:
            text += "┬"
    text += "┐" + "\n"
    
    for x, square in enumerate(args):
        for row in square:
            for i, column in enumerate(row):
                text += "│" + str(column) + " " * (col_widths[i] - len(str(column)))

            text += "│\n"
        if x == len(args) - 1:
            text += "└"
            for i in range(width):
                text += "─" * col_widths[i]
                if i != width - 1:
                    text += "┴"
            text += "┘" + "\n"
        else:
            text += "├"
            for i in range(width):
                text += "─" * col_widths[i]
                if i != width - 1:
                    text += "┼"
            text += "┤" + "\n"

    return text