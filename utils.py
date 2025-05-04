import time


def checkDict(dict_to_check,key_to_find, value_if_not_found):
    if key_to_find in dict_to_check:
        return dict_to_check[key_to_find]
    else:
        return value_if_not_found
    
def timeInteval():          #negeer deze, voorlopig niet gebruikt
    now = time.time()
    if prev_frame_time:
        dt = now - prev_frame_time 
        prev_frame_time = now
        print(now)
        yield dt
    else:
        prev_frame_time = now
        yield 1

class SelectionList:
    def __init__(self):
        self.list = []
        self.current_pos = 0

    def append(self,obj):
        self.list.append(obj)

    def remove(self,obj):
        self.list.remove(obj)

    def go_next(self):
        self.current = (self.current+1)% self.length

    def go_previous(self):
        self.current = (self.current-1)% self.length

    @property
    def length(self):
        return len(self.list)

    @property
    def next(self):
        return (self.current+1)% self.length
    
    @property
    def previous(self):
        return (self.current-1)% self.length
    
    @property
    def current(self):
        return self.list[self.current_pos]
    
    @current.setter
    def current(self, value: str):
        if value in self.list:
            self.current_pos = self.list.index(value)

