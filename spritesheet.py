import pygame

class Spritesheet:                  #getframe van video op youtube gehaald: https://www.youtube.com/watch?v=M6e3_8LHc7A
    def __init__(self, path, width, height):            #alle sprites op de spritesheet MOETEN dezelde dimensies hebben (neem dus een spritesheet per geanimeerde personnage/object)
        self.sheet = pygame.image.load(path).convert()
        self.frame_width = width
        self.frame_height = height

    def getFrame(self,column, row = 0, scale = 1):                             #row en comumn zijn voor de positie van de te nemen frame waarbij de spritesheet al verdeeld werd in vakjes, scale gaat waarschijnlijk nooit gebruikt worden aangezien we het in de object klasse al kunnen doen
        image = pygame.Surface((self.frame_width,self.frame_height))
        image.blit(self.sheet,(0,0),area=((column*self.frame_width),(row*self.frame_height),self.frame_width,self.frame_height))          #area: neemt enkel het aangeduide deel van de hele spritesheet met de twee eerste parameters de coordinaten van de linkerbovenhoek en de twee andere de braadte en hoogte van de te nemen oppervlakte
        image = pygame.transform.scale(image, (self.frame_width*scale, self.frame_height*scale))
        return image
    
    def makeAnimation(self, frames, column, row=0, direction = 'x'):      #row en culumn zijn voor de positie van de startframe
        animation = []

        if direction == 0 or direction=='x':
            frame = column
            for i in range(frames):
                animation.append(self.getFrame(frame+i, row))
        elif direction == 1 or direction=='y':
            frame = row
            for i in range(frames):
                animation.append(self.getFrame(column, frame+i))
        
        return animation


        """else: 
            print("Spritesheet.makeAnimation(): Wrong direction given")
            return 0"""