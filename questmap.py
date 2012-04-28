'''
Map module, all related to map management
'''

from utils import load_image


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.bricks = [[1] * width for i in range(height)]
        self.images = [0]
        self.objects = []
        self.scroll = [0, 0]

        self.block_names = [
            'Water Block.png',
            'Wall Block Tall.png',
            'Stone Block Tall.png',
            'Brown Block.png',
            'Dirt Block.png',
            'Grass Block.png',
            'Plain Block.png',
            'Stone Block.png',
            'Wall Block.png',
            'Wood Block.png',
        ]

        self.block_limit = 3

        for i in self.block_names:
            im, self.rect = load_image(i)
            self.images.append(im)

    def get_obj(self, name):
        for o in self.objects:
            if o.name == name:
                return o

        return None

    def rm_obj(self, name):
        o = self.get_obj(name)
        if o:
            self.objects.remove(o)

    def add(self, obj):
        self.objects.append(obj)

    def load_from_image(self, image):
        img, rect = load_image(image)
        self.width = rect.width
        self.height = rect.height - 1
        self.bricks = [[0] * self.width for i in range(self.height)]
        # first line color mapping
        mapping = {}
        for j in range(rect.width):
            color = img.get_at((j, 0))
            if color.a == 0:
                break

            mapping[(color.r, color.g, color.b, color.a)] = j + 1

        for i in range(1, rect.height):
            for j in range(rect.width):
                color = img.get_at((j, i))
                self.bricks[i - 1][j] = mapping.get((color.r, color.g, color.b, color.a), 0)

    def get_brick(self, i, j):
        si, sj = self.scroll
        i = i + si
        j = j + sj
        if i >= self.height or j >= self.width:
            return 0
        return self.bricks[i][j]

    def draw_brick(self, screen, i, j):
        self.rect.x = 100 * j
        self.rect.y = 80 * i
        idx = self.get_brick(i, j)
        if idx:
            screen.blit(self.images[idx], (self.rect.x, self.rect.y))

    def draw(self, screen):
        w, h = screen.get_size()
        if self.scroll[0]:
            i = -1
            for j in range((w // 100) + 1):
                self.draw_brick(screen, i, j)

        for i in range((h // 80) + 1):
            for j in range((w // 100) + 1):
                self.draw_brick(screen, i, j)

            for o in self.objects:
                x, y = o.map_pos()
                if y == i:
                    o.draw(screen)

        for o in self.objects:
            o.draw_text(screen)

    def can_move(self, obj):
        x, y = obj.screen_pos()
        if y >= len(self.bricks) or x >= len(self.bricks[0]) or x < 0 or y < 0:
            return False

        if self.bricks[y][x] > 3:
            return self.chech_collisions(obj)
        else:
            return False

    def chech_collisions(self, obj):
        for o in self.objects:
            if o == obj:
                continue
            if o.screen_pos() == obj.screen_pos():
                return o.collision(obj)

        return True

    def update(self, events):
        for o in self.objects:
            o.update(events)
