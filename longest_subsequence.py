def longest_common_subsequence(string_a, string_b):
    grid_rows = len(string_a)
    grid_columns = len(string_b)
    grid = [[0 for _ in range(grid_columns)] for _ in range(grid_rows)]

    for y in range(grid_rows):
        for x in range(grid_columns):
            upper_left_value = grid[y - 1][x - 1] if y > 0 and x > 0 else 0
            if string_a[y] == string_b[x]:
                grid[y][x] = upper_left_value + 1
            else:
                grid[y][x] = max(neighbor_values(grid, x, y))

    return grid[-1][-1]

def neighbor_values(grid, x, y):
    result = [0]
    if x > 0:
        result.append(grid[y][x - 1])
    if y > 0:
        result.append(grid[y - 1][x])
    return result
