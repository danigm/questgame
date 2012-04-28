import random


def random_movement(obj):
    goto = random.randint(0, 3)

    if goto == 0:
        obj.move_to(0, -1)
    elif goto == 1:
        obj.move_to(0, 1)
    elif goto == 2:
        obj.move_to(-1, 0)
    else:
        obj.move_to(1, 0)


def no_movement(obj):
    pass


class linear:
    def __init__(self, direction=1, steps=4):
        # direction: <- -1, -> 1, ^ -2, v 2
        self.direction = direction
        self.steps = steps
        self.step_count = 1

    def __call__(self, obj):
        if self.direction == -1:
            obj.move_to(-1, 0)
        elif self.direction == 1:
            obj.move_to(1, 0)
        elif self.direction == -2:
            obj.move_to(0, -1)
        elif self.direction == 2:
            obj.move_to(0, 1)

        self.step_count += 1

        if self.step_count == self.steps:
            self.step_count = 1
            self.direction = -self.direction


class circular:
    def __init__(self, steps=2):
        # direction: <- -1, -> 1, ^ -2, v 2
        self.direction = 1
        self.steps = steps
        self.step_count = 1

    def __call__(self, obj):
        if self.direction == -1:
            obj.move_to(-1, 0)
            nx = -2
        elif self.direction == 1:
            obj.move_to(1, 0)
            nx = 2
        elif self.direction == -2:
            obj.move_to(0, -1)
            nx = 1
        elif self.direction == 2:
            obj.move_to(0, 1)
            nx = -1

        self.step_count += 1

        if self.step_count == self.steps:
            self.step_count = 1
            self.direction = nx
