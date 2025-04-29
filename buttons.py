import pygame
from objects import Object

class Button(Object):
	def __init__(self, game, x, y, text, width = 100, height = 50, image = None):
		super().__init__(game,x,y,width,height,image)
		self.text = text


		fontsize = int(height/4)
		font = pygame.font.SysFont("monospace", fontsize)
		label = font.render(self.text,1, (0,0,0))
		text_size = font.size(self.text)
		self.texture.blit(label,(width/2-text_size[0]/2 , height/2-text_size[1]/2))

	def clicked(self):
		print('Im clicked!!')
		pass		#deze wordt pas bij de child classes gebruikt

	def checkClick(self):
		mouse = pygame.mouse.get_pressed()
		if mouse[0]:		#mouse[0] is de linker muisknop
			mouse_pos = pygame.mouse.get_pos()
			hitbox = self.hitbox
			if (mouse_pos[0]>hitbox["top"] and mouse_pos[0]<hitbox["bottom"]) and (mouse_pos[1]<hitbox["right"] and mouse_pos[1]>hitbox["left"]):
				self.clicked()
			
	def update(self):
		self.checkClick()
		super().update()

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
