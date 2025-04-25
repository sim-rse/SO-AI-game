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