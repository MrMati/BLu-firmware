from machine import Pin, PWM, ADC


# This module is responsible for interacting with real hardware
# It's designed so that it can be mocked easily

def init_hardware():
    init_led()
    init_sensor()


RED = 0
GREEN = 1
BLUE = 2
pwm_pins = [4, 3, 2]

pwms = []
adc: ADC | None = None


def init_led():
    global pwms

    # PWM is inverted for common anode LED
    pwms = [PWM(Pin(pwm_pins[c]), invert=True) for c in range(3)]
    [pwm.freq(1000) for pwm in pwms]
    [pwm.duty_u16(0) for pwm in pwms]


def init_sensor():
    global adc
    adc = ADC(Pin(28))


def read_sensor(num_samples: int = 1):
    if not adc:
        return None

    acc = 0
    for _ in range(num_samples):
        acc += adc.read_u16()

    return acc / num_samples


def set_led(color: int):
    r = (color >> 24) & 0xFF
    g = (color >> 16) & 0xFF
    b = (color >> 8) & 0xFF
    # a = (color & alphaMask)

    pwms[RED].duty_u16(int(257 * r))
    pwms[GREEN].duty_u16(int(257 * g))
    pwms[BLUE].duty_u16(int(257 * b))


def free_hardware():
    if pwms:
        pwms[RED].deinit()
        pwms[GREEN].deinit()
        pwms[BLUE].deinit()
