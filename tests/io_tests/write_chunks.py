# Stress Test:
# Write 8, 16 digit to 100 individual files

import time
from file_functs import write_chunks

start = time.time()
write_chunks(3000)
end = time.time()
print('Files created in %d milliseconds' % ((end - start) * 1000))
