import asyncio

class Callback:
    def __init__(self, fn, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        return self.fn(*self.args, *args, **self.kwargs, **kwargs)

class AsyncCallback(Callback):
    async def __call__(self, *args, **kwargs):
        return await self.fn(*self.args, *args, **self.kwargs, **kwargs)

class CallbackSource:
    events = ()

    def __init__(self):
        self.callbacks = {}
        for event in self.events:
            self.callbacks[event] = []

    def on(self, event, cb, *args, **kwargs):
        if type(cb).__name__ in ("function", "bound_method"):
            cb = Callback(cb, *args, **kwargs)
        if type(cb).__name__ == "generator":
            cb = AsyncCallback(cb, *args, **kwargs)

        self.callbacks[event].append(cb)

    def trigger(self, event, *args, **kwargs):
        tasks = [cb(*args, **kwargs) for cb in self.callbacks[event]]
        tasks = [task for task in tasks if task is not None]
        if len(tasks) == 0:
            return

        print("callback triggered",  self.__class__.__name__, event)
        asyncio.create_task(asyncio.gather(*tasks))

    async def trigger_async(self, event, *args, **kwargs):
        tasks = [cb(*args, **kwargs) for cb in self.callbacks[event]]
        tasks = [task for task in tasks if task is not None]
        if len(tasks) == 0:
            return []
        await asyncio.gather(*tasks)

