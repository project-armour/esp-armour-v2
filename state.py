"""Stores configuration and runtime data"""
from json import load, dump
from utils import *

class State(CallbackSource):
    """Stores runtime data"""
    events = ('set', )
    def __init__(self):
        """Initialize state"""
        super().__init__()
        with open('default_state.json') as configfile:
            self.state = load(configfile)

    def query(self, key, *args):
        """Get state information"""
        return self[key]

    def set(self, key, value, *args):
        """Set state information"""
        self[key] = value

    def __getitem__(self, item):
        """Get state information"""
        return self.state.get(item)

    def __setitem__(self, key, value):
        """Set state information"""
        self.state[key] = value
        self.trigger('set', key, value)


class Config:
    """Stores configuration"""
    def __init__(self):
        """Load configuration"""
        with open('config_default.json') as defaultconfig:
            self.config = load(defaultconfig)
        with open('config.json') as configfile:
            self.config.update(load(configfile))
        with open('config.json', 'w') as configfile:
            dump(self.config, configfile)

    def query(self, key, *args):
        """Get configuration value"""
        return self[key]

    def set(self, key, value, *args):
        """Set configuration value"""
        self[key] = value

    def __getitem__(self, item):
        """Get configuration value"""
        return self.config.get(item)

    def __setitem__(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        with open('config.json', 'w') as configfile:
            dump(self.config, configfile)

state = State()
config = Config()