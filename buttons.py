import pygame
from main import Object

class Button(Object):
	def __init__(self, game, x, y, text, width = 100, height = 50, image = None):
		super().__init__(game,x,y,width,height,image)
		self.text = text

	def clicked(self):
		pass

	def checkClick(self,mouse):
		hitbox = self.hitbox
		if (mouse[0]>hitbox["top"] and mouse[0]<hitbox["bottom"]) and (mouse[1]<hitbox["right"] and mouse[1]>hitbox["left"]):
			self.clicked()

class SceneButton(Button):
	def __init__(self, game, x, y, text, newScene, width=100, height=50, image=None):
		super().__init__(game, x, y, text, width, height, image)
		self.newScene = newScene
	
	def clicked(self):
		self.game.scene_running = False
		self.game.scene = self.newScene

class CharacterSelectButton(Button):
	def __init__(self, game, x, y, text, width=100, height=50, image=None):
		super().__init__(game, x, y, text, width, height, image)
