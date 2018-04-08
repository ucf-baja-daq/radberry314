# writer.py
# functions to handle all file writing

def writer(q, f, i):
    # open file for writing. overwrite existing data.
    file = open(f, "w")

    # empty string to hold chunks
    s = ""

    while q.recv() != "c":
        try:
            s += str(q.recv())
            print(s)
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

        except KeyboardInterrupt:
            print("exception")
            file.write(s)
            file.flush()
            file.close()
            break


    print("end")
    file.write(s)
    file.flush()
    file.close()
