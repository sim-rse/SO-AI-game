import time #tijd importeren zodat ze weten wat een seconde is 
from rich import print #het is een speciale printfunctie die met kleuren print
class Animations():
    def __init__(self):
        self.current = Animation('None animation', [None], False)       #current heeft een animatie nodig, dus er wordt een dummy animatie gemaakt zolang er geen nieuwe wordt afgespeeld
        #print("[blue]Current zou hier een keer moeten worden gemaakt")
        self.frame = 0

        self.fps = 15   # hoeveel frames per seconde
        self.lastFrameTime = 0

        self.animations = {}

        self.image = None

        self.default = 'default'

    def play(self, name, frame=0):
        if self.current.name == name:
            pass                        # de animatie speelt al dus niks doen
        elif name in self.animations:   #als het niet speelt dan start hij een animatie als het bestaat
            self.current = self.animations[name]
            #print(f"[[yellow]I[/yellow]] Nieuwe self.current: {self.current}")
            self.frame = frame

            self.image = self.current.frames[frame]
            self.lastFrameTime = time.time()
        else:
            print(f"[red]Animation: {name} not found!")

    def load(self, name:str, animation:list, loop = False, next = None):    # deze laadt een animatie en geeft het een naam
        if self.animations == {} or name == "default":
            self.setDefault(name)
        self.animations[name] = Animation(name, animation, loop, next)
        #print(f"[red]Laden van animatie: [green]{name}[/green] met naam van type:[green]{type(name)}[/green] en met lijst: [green]{animation}[/green]\nDit leidt tot vorming van [/red]{self.animations[name]}")
    
    def update(self):
        if time.time() - self.lastFrameTime >= 1/self.fps:
            if self.frame < self.current.length-1:
                self.frame += 1
            elif self.current.loop:
                self.frame = 0
            elif self.current.next:
                print(f"playing next animation: {self.current.next}")
                self.play(self.current.next)
            #print(f"updaten van {self.current} met frames {self.current.frames} op index {self.frame}")
            self.image = self.current.frames[self.frame]
            self.lastFrameTime = time.time()

    def setDefault(self, name):         #Hiermee kun je instellen wat de standaard animatie is Bijvoorbeeld: als er niks gebeurt, toon dan "default".
        self.default = name
    
class Animation():
    def __init__(self, name:str, frames:list, loop: bool, next:str = None):
        self.name = name
        self.frames = frames            #aantal frames

        self.loop = loop
        self.length = len(frames)
        self.next = next
        
    def __str__(self):
        return f"Animatie object met naam {self.name} en lengte {self.length}"