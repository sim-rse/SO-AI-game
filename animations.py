import time #tijd importeren zodat ze weten wat een seconde is 
from rich import print #rich.print wordt gebruikt om kleurrijke tekst naar de console te sturen.
class Animations():
    def __init__(self):
        self.current = Animation('None animation', [None], False)       #current heeft een animatie nodig, dus er wordt een dummy animatie gemaakt zolang er geen nieuwe wordt afgespeeld
        #print("[blue]Current zou hier een keer moeten worden gemaakt")
        self.frame = 0
        self.fps = 15   # hoeveel frames per seconde
        self.lastFrameTime = 0 #Tijd van de laatste frame update.
        self.animations = {}# Een woordenboek voor alle geladen animaties.
        self.image = None #huidige afbeelding van de animatie 
        self.default = 'default' #Naam van de standaardanimatie (als er niets anders gebeurt

    def play(self, name, frame=0):
        if self.current.name == name:
            pass                        # de animatie speelt al dus niks doen
        elif name in self.animations:   # Als de animatie bestaat, start deze.
            self.current = self.animations[name] # Zet de huidige animatie naar de opgegeven animatie.
            #print(f"[[yellow]I[/yellow]] Nieuwe self.current: {self.current}")
            self.frame = frame

            self.image = self.current.frames[frame] # Haal de afbeelding van dat frame.
            self.lastFrameTime = time.time()
        else:
            print(f"[red]Animation: {name} not found!")  # Als de animatie niet bestaat, geef een foutmelding.

    def load(self, name:str, animation:list, loop = False, next = None):    # deze laadt een animatie en geeft het een naam
        if self.animations == {} or name == "default":
            self.setDefault(name)  # Zet de default animatie als er geen animaties zijn.
        self.animations[name] = Animation(name, animation, loop, next) # Laad de animatie in de dictionary.
        #print(f"[red]Laden van animatie: [green]{name}[/green] met naam van type:[green]{type(name)}[/green] en met lijst: [green]{animation}[/green]\nDit leidt tot vorming van [/red]{self.animations[name]}")
    
    def update(self):
        if time.time() - self.lastFrameTime >= 1/self.fps:# Als het tijd is voor het volgende frame.
            if self.frame < self.current.length-1:
                self.frame += 1 # Ga naar het volgende frame
            elif self.current.loop:
                self.frame = 0 # Herhaal de animatie als 'loop' True is.
            elif self.current.next:
                print(f"playing next animation: {self.current.next}") # Speel de volgende animatie af.
                self.play(self.current.next)
            #print(f"updaten van {self.current} met frames {self.current.frames} op index {self.frame}")
            self.image = self.current.frames[self.frame] #update de afbeelding van het huidige frame.
            self.lastFrameTime = time.time() #update de tijd

    def setDefault(self, name):         #Hiermee kun je instellen wat de standaard animatie is Bijvoorbeeld: als er niks gebeurt, toon dan "default".
        self.default = name

    def playDefault(self):
        self.play(self.default)
    
class Animation():
    def __init__(self, name:str, frames:list, loop: bool, next:str = None):
        self.name = name
        self.frames = frames            #aantal frames

        self.loop = loop
        self.length = len(frames) # Het aantal frames in de animatie
        self.next = next
        
    def __str__(self): #str geeft een stringweergave van de animatie, die de naam en de lengte van de animatie bevat
        return f"Animatie object met naam {self.name} en lengte {self.length}" 