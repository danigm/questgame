class Event:
    def __init__(self, name):
        self.name = name
        self.listeners = {}

    def add(self, function, data=None):
        self.listeners[function] = data

    def delete(self, function):
        self.listeners.pop(function)

    def called(self, data=None):
        for function, d in self.listeners.items():
            if data is None:
                if d is None:
                    function()
                else:
                    if type(d) == type([]):
                        function(*d)
                    elif type(d) == type({}):
                        function(**d)
                    else:
                        function(d)
            else:
                if type(data) == type([]):
                    function(*data)
                elif type(data) == type({}):
                    function(**data)
                else:
                    function(data)


class EventManager:
    def __init__(self):
        self.events = {}

    def add_event(self, Event):
        self.events[Event.name] = Event

    def del_event(self, Event):
        self.events.pop(Event.name)

    def connect(self, event, function, data=None):
        self.events[event].add(function, data)

    def disconnect(self, event, function):
        self.events[event].delete(function)

    def signal(self, event, data=None):
        if data is None:
            self.events[event].called()
        else:
            self.events[event].called(data)
