# coding=utf-8
from future import Future


class SystemCall(Future):
    """
    System Call base class. All system operations will be
    implemented by inheriting from this class
    """

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


# Create a new task
class NewTask(SystemCall):
    def __init__(self, target):
        self.target = target

    def __call__(self, *args, **kwargs):
        tid = self.scheduler.create_task(self.target)
        self.set_result(tid)


class _Wait_Stream(SystemCall):
    def __init__(self, f):
        if hasattr(f, "fileno"):
            self.f = f.fileno()
        else:
            self.f = f


# Wait for reading
class ReadWait(_Wait_Stream):
    def __call__(self, *args, **kwargs):
        self.scheduler.wait_for_read(self.f, self.set_result, True)


# Wait for writing
class WriteWait(_Wait_Stream):
    def __call__(self, *args, **kwargs):
        self.scheduler.wait_for_write(self.f, self.set_result, True)
