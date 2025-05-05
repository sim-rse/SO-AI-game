class DeathArea:
    def __init__(self, game, top, bottom, left, right):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

        self.game = game

    def update(self):
        for ent in self.game.entities:
            if (ent.pos.y > self.top or ent.pos.y < self.bottom) or (ent.pos.x < self.left or ent.pos.x > self.right):
                ent.die()