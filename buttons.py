import pygame
from objects import Object

class Button(Object):
	def __init__(self, game, x, y, text, width = 100, height = 50, color = (0,0,200), border_color = None, image = None, scale = 1):
		super().__init__(game,x,y,width,height,image = image, color = color, scale = 1)
		self.text = text
		self.color = color
		self.border_color = border_color
		self.hoverColor = tuple([i+10 if i+10 <= 255 else 255 for i in color])
					
		fontsize = int(height/2)
		self.font = pygame.font.SysFont("monospace", fontsize)

		self.update_texture()
		

	def update_texture(self):
		if self.checkHover():
			color = self.hoverColor
		else:
			color = self.color

		if self.border_color:
			self.texture.fill(self.border_color)
			border = self.height*0.05

			pygame.draw.rect(self.texture, color, (border, border, self.width-border, self.height-border))
		else:
			self.texture.fill(color)

		label = self.font.render(self.text,1, (0,0,0))
		text_size = self.font.size(self.text)
		self.texture.blit(label,(self.width/2-text_size[0]/2 , self.height/2-text_size[1]/2))

	def clicked(self):
		pass		#deze wordt pas bij de child classes gebruikt

	def checkClick(self):
		mouse = pygame.mouse.get_pressed()
		if mouse[0]:		#mouse[0] is de linker muisknop
			mouse_pos = pygame.mouse.get_pos()
			hitbox = self.hitbox
			if (mouse_pos[1]>hitbox["top"] and mouse_pos[1]<hitbox["bottom"]) and (mouse_pos[0]<hitbox["right"] and mouse_pos[0]>hitbox["left"]):
				self.clicked()

	def checkHover(self):
		mouse_pos = pygame.mouse.get_pos()
		hitbox = self.hitbox
		if (mouse_pos[1]>hitbox["top"] and mouse_pos[1]<hitbox["bottom"]) and (mouse_pos[0]<hitbox["right"] and mouse_pos[0]>hitbox["left"]):
			return True
		else:
			return False
		
	def update(self):
		self.checkClick()
		self.update_texture()
		super().update()

class SceneButton(Button):
	def __init__(self, game, x, y, text, newScene, width=100, height=50, color = (0,200,0), border_color = None, image= None, scale = 1):
		super().__init__(game, x, y, text, width, height, color, border_color, image, scale)
		self.newScene = newScene
	
	def clicked(self):
		self.game.scene_running = False
		self.game.scene = self.newScene

class CharacterSelectButton(Button):
	def __init__(self, game, x, y, text, width=100, height=50, color = (200,0,0), border_color = None, image = None, scale = 1, character = None):
			super().__init__(game, x, y, text, width, height, color, border_color, image, scale)
			self.character = character

	def clicked(self):
		self.game.character = self.character
	
class PauseButton(Button):
	def __init__(self, game, x, y, text, width=100, height=50, color=(0, 0, 200), border_color=None, image=None, scale=1):
		super().__init__(game, x, y, text, width, height, color, border_color, image, scale)

	def clicked(self):
		self.game.pause()
