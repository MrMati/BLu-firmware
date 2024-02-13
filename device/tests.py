from machine import Pin, PWM, ADC, lightsleep
import sys
import time
import gc
import os
import micropython

def set_safe_exit():
    pin = Pin(15, Pin.IN, Pin.PULL_UP)

    @micropython.asm_thumb
    def callback():
        wfi()

    pin.irq(trigger=Pin.IRQ_FALLING, handler=callback)


def sleep_test():
    set_safe_exit()

    while True:
        lightsleep(10)





def free():
    gc.collect()
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F + A
    P = '{0:.2f}%'.format(F / T * 100)
    return ('Total: {0} Free: {1} ({2})'.format(T, F, P))


def df():
    s = os.statvfs('//')
    print(s)
    return ('{0} MB'.format((s[0] * s[3]) / 1048576))




scalar = float # a scale value (0.0 to 1.0)
def hsv_to_rgb( h:scalar, s:scalar, v:scalar, a:scalar =1.0) -> tuple:
    if s:
        if h == 1.0: h = 0.0
        i = int(h*6.0); f = h*6.0 - i
        
        w = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        
        if i==0: return (v, t, w, a)
        if i==1: return (q, v, w, a)
        if i==2: return (w, v, t, a)
        if i==3: return (w, q, v, a)
        if i==4: return (t, w, v, a)
        if i==5: return (v, w, q, a)
    else: return (v, v, v, a)

    print("here")


def led_test():
    RED = 0
    GREEN = 1
    BLUE = 2

    # Declare pins
    pwm_pins = [2,3,4]
    # Setup pins for PWM
    pwms = [PWM(Pin(pwm_pins[c]), invert=True) for c in range(3)]
    # Set pwm frequency
    [pwm.freq(1000) for pwm in pwms]


    def pwm_duty(pwm: PWM, val: float):
        pwm.duty_u16(int(65535 * val))

    # Deinitialize PWM on all pins
    def deinit_pwm_pins():
        pwms[RED].deinit()
        pwms[GREEN].deinit()
        pwms[BLUE].deinit()

    

    def loop():
        counter = 0
        while True:
            numColors = 255
            colorNumber = counter - numColors if counter > numColors else counter;
  
            # Play with the saturation and brightness values
            # to see what they do
            saturation = 1; # Between 0 and 1 (0 = gray, 1 = full color)
            brightness = 0.1; # Between 0 and 1 (0 = dark, 1 is full brightness)
            hue = (colorNumber / float(numColors)) ; # Number between 0 and 1
            r, g, b, _ =  hsv_to_rgb(hue, saturation, brightness); 
            
            pwms[RED].duty_u16(int(65535 * r))
            pwms[GREEN].duty_u16(int(65535 * g))
            pwms[BLUE].duty_u16(int(65535 * b))
            
            # Counter can never be greater then 2 times the number of available colors
            # the colorNumber = line above takes care of counting backwards (nicely looping animation)
            # when counter is larger then the number of available colors
            counter = (counter + 1) % (numColors * 2);
            
            # If you uncomment this line the color changing starts from the
            # beginning when it reaches the end (animation only plays forward)
            # counter = (counter + 1) % (numColors);

            time.sleep(0.01)
    
    """
    pwms[GREEN].duty_u16(0)
    pwms[BLUE].duty_u16(0)
    
    adc = ADC(Pin(28))    
          
    def loop():
        while True:
            reading = adc.read_u16()
            val = reading//3
            print(val)
            pwms[RED].duty_u16(val)
            time.sleep_ms(10)
    """
    try:
        loop()
    except KeyboardInterrupt:
        deinit_pwm_pins()


led_test()