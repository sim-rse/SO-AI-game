import pygame

# Deze klasse wordt gebruikt om een spritesheet in te laden en frames te extraheren
class Spritesheet:                  #getframe van video op youtube gehaald: https://www.youtube.com/watch?v=M6e3_8LHc7A
    def __init__(self, path, width, height, colorkey = (0,0,0)):            #alle sprites op de spritesheet MOETEN dezelde dimensies hebben (neem dus best een spritesheet per animatie OF per geanimeerde personnage/object als zijn groote niet verandert)
        #path: bestandsnaam of pad naar de spritesheet
        self.sheet = pygame.image.load(path).convert()  #convert converteert naar de goede dimensies (black magic)
        self.frame_width = width
        self.frame_height = height
        self.colorkey = colorkey

    def getFrame(self,column, row, scale):                             #row en comumn zijn voor de positie van de te nemen frame waarbij de spritesheet al verdeeld werd in vakjes, scale gaat waarschijnlijk nooit gebruikt worden aangezien we het in de object klasse al kunnen doen
        image = pygame.Surface((self.frame_width,self.frame_height)) #Maakt een leeg canvas (oppervlak) ter grootte van één frame.
        image.blit(self.sheet,(0,0),area=((column*self.frame_width),(row*self.frame_height),self.frame_width,self.frame_height))        #kopieert een stuk van de spritesheet naar image  #area: neemt enkel het aangeduide deel van de hele spritesheet met de twee eerste parameters de coordinaten van de linkerbovenhoek en de twee andere de braadte en hoogte van de te nemen oppervlakte
        #print(f"de scale is: {scale}")
        image = pygame.transform.scale(image, (self.frame_width*scale, self.frame_height*scale))
        image.set_colorkey(self.colorkey)
        return image
    
    def makeAnimation(self, frames, column, row=0, direction = 'x', scale = 1):      #row en culumn zijn voor de positie van de startframe, de direction vertelt hoe de programma frames gaat zoeken: horizontaal of verticaal
        animation = []

        if direction == 0 or direction=='x':
            frame = column
            for i in range(frames):
                animation.append(self.getFrame(frame+i, row, scale)) #Pakt frames van links naar rechts (bijv. kolom 0, 1, 2, ...).
        elif direction == 1 or direction=='y':
            frame = row
            for i in range(frames):
                animation.append(self.getFrame(column, frame+i, scale))#Pakt frames van boven naar onder (bijv. rij 0, 1, 2, ...).
        
        return animation #Return: Een lijst animation van Surface objecten die samen een animatie vormen.
