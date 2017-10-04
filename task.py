# coding=utf-8


class Task:
    _taskid = 0

    def __init__(self, target):
        self.__class__._taskid += 1
        self.tid = Task._taskid
        self.target = target
        self.callback_list = []

    def __call__(self, *args, **kwargs):
        print("resumes running task", self.target.gi_code.co_name, self.tid)
        return self.target.send(None)

    def add_done_callback(self, cb):
        self.callback_list.append(cb)
