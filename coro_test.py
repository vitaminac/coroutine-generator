# coding=utf-8
from coroutine import broadcast, coroutine


def simple_coro():
    print("coro1 part 1:", f"i m coro {yield}")
    print("coro1 part 2:", f"i m coro {yield}")


@coroutine
def calling_simple_multi_time():
    yield from simple_coro()
    print("first time calling simple coro completed")
    yield from simple_coro()
    print("second time calling simple coro completed")


def simple_coro_calling_system_call():
    print("yield a simple system call GetID")
    tid = yield from GetTid()
    # processed
    return format(tid, '02x')


def log_with_taskid(id, targets):
    target = broadcast(targets)
    try:
        while True:
            item = (yield)
            print(f"task {id} received ", item)
            target.send(id)
    except StopIteration:
        pass


def test_coro1():
    tid = yield from simple_coro_calling_system_call()
    yield from send_seed(log_with_taskid(tid, [calling_simple_multi_time(), calling_simple_multi_time()]))
    yield tid + "terminated"


n = 0


def send_seed(target):
    global n
    item = None
    next(target)
    while True:
        n += 1
        yield target.send(n)
