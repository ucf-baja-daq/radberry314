# writer.py
# functions to handle all file writing

import logging

def writer(data_comm, file_name, chunk_size, log_file_handler, log_stream_handler):
    logger = logging.getLogger(__name__)
    logger.addHandler(log_file_handler)
    logger.addHandler(log_stream_handler)

    logger.info("Begin data logging to {}".format(file_name))

    # open file for writing. overwrite existing data.
    file = open(file_name, "w")

    # empty string to hold chunks
    s = ""

    while data_comm.recv() != "c":
        try:
            s += str(data_comm.recv())
            print(s)
            # print("recieve" + s)
            if len(s) > chunk_size:
                # print("writing)")
                file.write(s)
                file.flush()
                s = ""

        # if comm sender closes, recv() will throw EOFError, but it hasn't worked here yet. It will remain here for safety.
        except EOFError:
            logger.exception("Data sender closed comms.")
            break

    logger.info("End data logging to {}".format(file_name))

    file.write(s)
    file.flush()
    file.close()
