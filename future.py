# coding=utf-8
class Future:
    def set_waiter(self, scheduler, waiter):
        self.scheduler = scheduler
        self.waiter = waiter

    def set_result(self, result = None):
        self.result = result
        self.wakeUp_waiter()

    def wakeUp_waiter(self):
        self.scheduler.schedule(self.waiter)

    def __iter__(self):
        yield self
        return self.result

