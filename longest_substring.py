def longest_common_substring(string_a, string_b):
    grid_rows = len(string_a)
    grid_columns = len(string_b)
    grid = [[0 for _ in range(grid_columns)] for _ in range(grid_rows)]
    max = 0

    for y in range(grid_rows):
        for x in range(grid_columns):
            upper_left_value = grid[y - 1][x - 1] if y > 0 and x > 0 else 0
            if string_a[y] == string_b[x]:
                grid[y][x] = upper_left_value + 1
                if grid[y][x] > max:
                    max = grid[y][x]
            else:
                grid[y][x] = 0

    return max