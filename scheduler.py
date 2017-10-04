# coding=utf-8

from queue import Queue
from select import select

from future import Future
from simple_server import server
from systemcall import SystemCall
from task import Task


class Scheduler(object):
    def __init__(self):
        # a queue of tasks that are ready to run
        self.ready = Queue()
        # A dictionary that keeps track of all active tasks (each task has a unique integer task ID)
        self.task_map = { }
        # Holding ares for tasks blocking on I/O.
        # These are dictionaries mapping file descriptors to tasks
        self.read_waiting = { }
        self.write_waiting = { }

    @staticmethod
    def _wait_for(waiting_list, fd, cb, *args, **kwargs):
        try:
            waiting_list[fd].append((cb, args, kwargs))
        except KeyError:
            waiting_list[fd] = [(cb, args, kwargs)]

    def wait_for_read(self, fd, cb, *args, **kwargs):
        # Function that simply put a task into one of the above dictionaries
        self._wait_for(self.read_waiting, fd, cb, *args, **kwargs)

    def wait_for_write(self, fd, cb, *args, **kwargs):
        self._wait_for(self.write_waiting, fd, cb, *args, **kwargs)

    def io_poll(self, timeout = 0):
        while True:
            # I/O Polling. Use select() to determine
            # which file descriptors can be used. Unblock any associated task
            if self.ready.empty():
                timeout = None
            else:
                timeout = 0
            if self.read_waiting or self.write_waiting:
                read_ready, write_ready, error = select(self.read_waiting.keys(), self.write_waiting.keys(), [], timeout)
                for fd in read_ready:
                    for cb, args, kwargs in self.read_waiting.pop(fd):
                        cb(*args, **kwargs)
                for fd in write_ready:
                    for cb, args, kwargs in self.write_waiting.pop(fd):
                        cb(*args, **kwargs)
            yield

    def create_task(self, target):
        """
        introduces a new task to the scheduler
        :param target:
        :type generator: a yield function or iterable object
        :return: the taskid of newly created task
        :rtype: integer
        """
        new_task = Task(target)
        self.task_map[new_task.tid] = new_task  # add to task map
        self.schedule(new_task)
        return new_task.tid

    def schedule(self, task):
        # Put a task onto the ready queue. This makes it available to run
        self.ready.put(task)

    def exit(self, task):
        # Remove the task from the scheduler's task map
        print(f"Task {task.tid} terminated")
        del self.task_map[task.tid]

    def run_forever(self):
        """
        Tha main scheduler loop. It pulls tasks off the queue and runs them to next yield
        :return:
        :rtype:
        """
        self.create_task(self.io_poll()) # Launch I/O polls
        while self.task_map:
            task = self.ready.get()
            try:
                result = task()
            except StopIteration:
                # Catch task exit and cleanup
                self.exit(task)
            else:
                # Look at the result yielded by the task if it's a SystemCall,
                # do some setup and run the system call on behalf of the task
                if isinstance(result, Future):
                    result.set_waiter(self, task)
                    if isinstance(result, SystemCall):
                        result()
                else:
                    self.schedule(task)


scheduler = Scheduler()
scheduler.create_task(server())
scheduler.run_forever()
