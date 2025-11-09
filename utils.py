"""General utilities"""

import asyncio

class Callback:
    """Class for callbacks"""
    def __init__(self, fn, *args, **kwargs):
        """Initializes callback"""
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        """Calls callback function"""
        return self.fn(*self.args, *args, **self.kwargs, **kwargs)

class AsyncCallback(Callback):
    """Class for async callbacks"""
    async def __call__(self, *args, **kwargs):
        """Calls async callback"""
        return await self.fn(*self.args, *args, **self.kwargs, **kwargs)

class CallbackSource:
    """Emits callbacks"""
    events = ()
    eventdebug = False

    def __init__(self):
        """Initializes callback emitter"""
        self.callbacks = {}
        for event in self.events:
            self.callbacks[event] = []

    def on(self, event, cb, *args, **kwargs):
        """Register a callback"""
        if type(cb).__name__ in ("function", "bound_method"):
            cb = Callback(cb, *args, **kwargs)
        if type(cb).__name__ == "generator":
            cb = AsyncCallback(cb, *args, **kwargs)

        self.callbacks[event].append(cb)

    def trigger(self, event, *args, **kwargs):
        """Trigger callbacks for event"""
        if self.eventdebug:
            print("triggered", event, *args, **kwargs)
        tasks = [cb(*args, **kwargs) for cb in self.callbacks[event]]
        tasks = [task for task in tasks if task is not None]
        if len(tasks) == 0:
            return

        print("callback triggered",  self.__class__.__name__, event)
        asyncio.create_task(asyncio.gather(*tasks))

    async def trigger_async(self, event, *args, **kwargs):
        """Triger callbacks for event asynchronously"""
        tasks = [cb(*args, **kwargs) for cb in self.callbacks[event]]
        tasks = [task for task in tasks if task is not None]
        if len(tasks) == 0:
            return []
        await asyncio.gather(*tasks)

