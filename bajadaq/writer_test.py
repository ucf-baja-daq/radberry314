import multiprocessing as mp
from time import time, sleep

def generator(a, b, f, i):
    w = mp.Process(target=writer, args=(b,f,i,))
    w.start()

    for i in range(10):
        # print("generating")
        a.send(''.join(['a' * 10] * 10))

    a.close()
    w.join()

def writer(q, f, i):
    s = ""

    # sleep(0.01)

    while q.poll():
        try:
            s += str(q.recv())
            # print("recieve" + s)
            if len(s) > i:
                # print("writing)")
                open(f, 'a').write(s)
                s = ""
        except EOFError:
            print("exception")
            open(f, 'a').write(s)
            break

    open(f, 'a').write(s)

if __name__ == "__main__":
    #freeze_support()
    for i in range(50000,200000,20000):
        average = 0
        for j in range(100):
            chunk = i

            a, b = mp.Pipe()

            f = "file.txt"

            open(f, "w")

            start = time()

            g = mp.Process(target=generator, args=(a, b, f, chunk,))

            g.start()

            g.join()

            average += time() - start

        print("{:>6}: {:.3f}".format(i,average / 100))
