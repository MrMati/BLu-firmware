import machine

# fully turns off common anode LED

pins_high = [2, 3, 4]
for pin_num in pins_high:
    pin = machine.Pin(pin_num, machine.Pin.OUT)
    pin.high()