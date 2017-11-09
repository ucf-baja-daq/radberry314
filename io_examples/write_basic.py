# Stress Test:
# Write 8, 16 digit to 100 individual files

import time
from file_functs import write_files

start = time.time()
write_files()
end = time.time()
print('Files created in %d milliseconds' % ((end - start) * 1000))
