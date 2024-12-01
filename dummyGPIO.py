#Raspberry Pi実機ではないとき、GPIOライブラリの代わりに使用
BCM = 'BCM'
IN = 'input'
OUT = 'output'
HIGH = True
LOW = False

def setmode(mode):
    # とりあえずprint
    print(f'GPIO mode: {mode}')

def setup(pin, mode):
    # とりあえずprint
    print(f'PIN({pin}) mode: {mode}')
    
def output(pin, state):
    # とりあえずprint
    print(f'PIN({pin}) state: {state}')

def input(pin):
#    str_state = input('state[HIGH/LOW]')
#    if str_state == 'HIGH':
#        state = HIGH
#    else:
#        state = LOW
    state = LOW
    # とりあえずprint
    print(f'PIN({pin}) state: {state}')
    return state

