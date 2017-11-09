import os

directory = 'files/'
file_name = 'fileteration'
num_files = 100


def clean_files():
    for fileiteration in range(num_files):
        file = '%s%s%d.txt' % (directory, file_name, fileiteration)
        os.remove(file)


def write_files():
    for fileiteration in range(num_files):
        file = '%s%s%d.txt' % (directory, file_name, fileiteration)

        f = open(file, 'w')

        for x in range(100000000000000000, 100000000000010000):
            f.write('%d, %d,%d,%d,%d,%d,%d,%d\n' %
                    (x, x + 1, x + 2, x + 3, x + 4, x + 5, x + 6, x + 7))


def write_files_with():
    for fileiteration in range(num_files):
        file = '%s%s%d.txt' % (directory, file_name, fileiteration)

        with open(file, 'w') as f:
            for x in range(100000000000000000, 100000000000010000):
                f.write('%d, %d,%d,%d,%d,%d,%d,%d\n' %
                        (x, x + 1, x + 2, x + 3, x + 4, x + 5, x + 6, x + 7))


def write_chunks(chunk_size):
    num_pins = 7
    num_data_points = num_pins + 1  # +1 for time
    if chunk_size is None:
        chunk_size = 100

    for fileiteration in range(num_files):
        file = '%s%s%d.txt' % (directory, file_name, fileiteration)

        with open(file, 'w') as f:
            buf = [num_data_points][chunk_size]
            for x in range(100000000000000000, 100000000000010000):
                if ((x + 1) % chunk_size) == 0:
                    f.write(join_data_points(buf))

# Write to buffer then convert to string once buffer is full
# Skip buffer and concatenate to string and write string


def join_array_to_string(array, delimiter):
    return delimiter.join(['{val}' for val in array])


def join_data_points(data_points):
    for row_index in len(data_points):
        data_points[row_index] = join_array_to_string(
            data_points[row_index], ',')
    return join_array_to_string(data_points, ';')
