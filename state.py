from json import load, dump
from utils import *

class State(CallbackSource):
    events = ('set', )
    def __init__(self):
        super().__init__()
        with open('default_state.json') as configfile:
            self.state = load(configfile)

    def query(self, key, *args):
        return self[key]

    def set(self, key, value, *args):
        self[key] = value

    def __getitem__(self, item):
        return self.state.get(item)

    def __setitem__(self, key, value):
        self.state[key] = value
        self.trigger('set', key, value)


class Config:
    def __init__(self):
        with open('config.json') as configfile:
            self.config = load(configfile)

    def query(self, key, *args):
        return self[key]

    def set(self, key, value, *args):
        self[key] = value

    def __getitem__(self, item):
        return self.config.get(item)

    def __setitem__(self, key, value):
        self.config[key] = value
        with open('config.json', 'w') as configfile:
            dump(self.config, configfile)

state = State()
config = Config()