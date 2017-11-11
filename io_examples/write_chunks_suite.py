# An examination of what size chunks work the best
# Ideally run this on a system capable of bearing the load test
# A normal computer will take seconds.. a rpi.. maybe a few minutes

import time
import sys
from file_functs import write_chunks

num_runs_per_chunk = 10
chunk_sizes = [1000, 2000, 3000,  4000, 5000, 6000, 7000, 8000, 9000]
times = []

print('Starting test suite')

for chunk_size in chunk_sizes:
    print('Running chunk size: %d' % (chunk_size))
    for test_num in range(num_runs_per_chunk):
        start = time.time()
        write_chunks(chunk_size)
        end = time.time()
        duration = end - start
        times.append(duration)
        # print('chunk size: %d  duration: %f' % (chunk_size,duration))
        # print('start: %s' % (start))
        # print('end: %s' % (end))

print('Test suite complete.')
print('Time analysis:')

for chunk_index in range(len(chunk_sizes)):
    time_len = times[chunk_index]
    longest = 0
    shortest = 1000000000000
    sum = 0

    # print('calculating range [%d,%d]' % (chunk_index * num_runs_per_chunk,
    #                                      chunk_index * num_runs_per_chunk + num_runs_per_chunk))
    for i in range(
            chunk_index * num_runs_per_chunk,
            chunk_index * num_runs_per_chunk + num_runs_per_chunk):
        if times[i] > longest:
            longest = times[i]
        if times[i] < shortest:
            shortest = times[i]
        sum += times[i]

    average = sum / num_runs_per_chunk

    print(
        'chunk size: %f \n\
            average:  %f \n\
            shortest: %f \n\
            longest:  %f'
        % (chunk_sizes[chunk_index % num_runs_per_chunk], average, shortest, longest))
