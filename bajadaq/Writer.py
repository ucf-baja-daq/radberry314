# Writer.py
# functions to handle all file writing

def writer(q, f, i):
    # open file for writing. overwrite existing data.
    file = open(f, "w")

    # empty string to hold chunks
    s = ""

    while q.poll():
        try:
            s += str(q.recv())
            # print("recieve" + s)
            if len(s) > i:
                # print("writing)")
                file.write(s)
                file.flush()
                s = ""
        except EOFError:
            print("exception")
            file.write(s)
            file.flush()
            file.close()
            break

    file.write(s)
    file.flush()
    file.close()
