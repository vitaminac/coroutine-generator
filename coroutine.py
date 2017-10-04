# coding=utf-8
# import asyncio


def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr

    return start


@coroutine
def grep(pattern, target):
    print("Looking for %s" % pattern)
    try:
        while True:
            line = (yield)  # receive an item
            if pattern in line:
                # send it along to the next stage
                target.send(line)
    except GeneratorExit:
        print("exiting")


def follow(file, target):
    with open(file, "r") as f:
        line = f.readline()
        while line:
            target.send(line)
            line = f.readline()
        target.close()


@coroutine  # end
def printer():
    try:
        while True:
            line = (yield)  # Receive an item
            print(line)
    except GeneratorExit:
        # done
        pass


@coroutine
def broadcast(targets):
    while targets:
        item = (yield)
        temp = targets[:]  # deep copy the targets list
        for target in temp:
            try:
                target.send(item)
            except StopIteration:
                targets.remove(target)


class GrepHandler:
    def __init__(self, pattern, target):
        self.pattern = pattern
        self.target = target

    def send(self, line):
        if self.pattern in line:
            self.target.send(line)


@coroutine
def threaded(target):
    messages = Queue()

    def run_target():
        while True:
            item = messages.get()
            if item is GeneratorExit:
                target.close()
                return
            else:
                target.send(item)

    Thread(target=run_target).start()
    try:
        while True:
            item = (yield)
            messages.put(item)
    except GeneratorExit:
        messages.put(GeneratorExit)


@coroutine
def sendto(f):
    try:
        while True:
            item = (yield)
            pickle.dump(item, f)
            f.flush()
    except StopIteration:
        f.close()


def recvfrom(f, target):
    try:
        while True:
            item = pickle.load(f)
            target.send(item)
    except EOFError:
        target.close()


@coroutine
def find_function():
    p = printer()
    target = broadcast([grep("def", p), grep("yield", p)])

    while True:
        item = (yield)
        target.send(item)

# follow("coroutine.py", find_function())
