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
            r = x + 0.0000000000000001
            f.write('%d,%d,%d,%d,%d,%d,%d,%d\n' %
                    (r, r + 1, r + 2, r + 3, r + 4, r + 5, r + 6, r + 7))


def write_files_with():
    for fileiteration in range(num_files):
        file = '%s%s%d.txt' % (directory, file_name, fileiteration)

        with open(file, 'w') as f:
            for x in range(100000000000000001, 100000000000010000):
                r = x + 0.0000000000000001
                f.write('%d, %d,%d,%d,%d,%d,%d,%d\n' %
                        (r, r + 1, r + 2, r + 3, r + 4, r + 5, r + 6, r + 7))


def write_chunks(chunk_size):
    num_pins = 7
    num_data_points = num_pins + 1  # +1 for time
    if chunk_size is None:
        chunk_size = 100

    for fileiteration in range(num_files):
        path = '%s%s%d.txt' % (directory, file_name, fileiteration)

        with open(path, 'w') as f:
            buf = []
            buf.append(['Time (s)', 'Channel 0', 'Channel 1', 'Channel 2',
                        'Channel 3', 'Channel 4', 'Channel 5', 'Channel 6', 'Channel 7'])

            for x in range(100000000000000001, 100000000000010000):
                r = x + 0.0000000000000001
                buf.append([r, r + 1, r + 2, r + 3,
                            r + 4, r + 5, r + 6, r + 7])
                if (x % chunk_size) == 0:
                    # print('writing data for x=%s' % (x - 100000000000000000))
                    f.write(join_data_points(buf))
                    buf = []


def join_array_to_string(array, delimiter):
    return delimiter.join(['{val}' for val in array])


def join_data_points(data_points):
    for row_index in range(0, len(data_points) - 1):
        # print('row_index: %d data_points[%d]: %s' % (
            # row_index, row_index, str(data_points[row_index + 1])))
        data_points[row_index] = join_array_to_string(
            data_points[row_index],
            ','
        )
    return join_array_to_string(data_points, ',\n')
