import asyncio

from machine import Pin, PWM, ADC
from utils import Enum, ThreadSafeEvent

# This module is responsible for interacting with real hardware
# It's designed so that it can be mocked easily
print("hardware global runs")


def init_hardware():
    init_led()
    init_sensor()
    init_plug_detection()
    init_buttons()


RED = 0
GREEN = 1
BLUE = 2
pwm_pins = [4, 3, 2]
pwms: list[PWM] = []

sensor_lock = asyncio.Lock()

sensor_adc: ADC | None = None
detect_adc: ADC | None = None

button_pins = [0, 1]
buttons: list[Pin] = []


def init_led():
    global pwms

    # PWM is inverted for common anode LED
    pwms = [PWM(Pin(pwm_pin), invert=True) for pwm_pin in pwm_pins]
    [pwm.duty_u16(0) for pwm in pwms]
    [pwm.freq(1000) for pwm in pwms]


def init_sensor():
    global sensor_adc
    sensor_adc = ADC(Pin(28))


def init_plug_detection():
    global detect_adc
    detect_adc = ADC(Pin(27))


def init_buttons():
    global buttons
    for button_pin in button_pins:
        button = Pin(button_pin, mode=Pin.IN)
        buttons.append(button)
        button.irq(trigger=Pin.IRQ_RISING, handler=lambda p, b_pin=button_pin: button_callback(b_pin))


button_event = ThreadSafeEvent(-1)


def button_callback(pin: Pin):
    if pin == 0:
        print("button pressed up")
    elif pin == 1:
        print("button pressed down")
    if pin == 0 or pin == 1:
        button_event.set(pin)


# EXPERIMENTAL DETECT IMPLEMENTATION
# can we do better than polling?
# consider digital interrupts

# SensorState should be moved to some hardware api def file
class SensorState(Enum):
    Unknown = -1
    Disconnected = 0  # 3.3V
    LightIntensity = 1  # ~0.58V
    Hall = 2
    Temperature = 3


def perform_detection() -> None | SensorState:
    if not sensor_adc:
        return None

    def is_around(mid: float, val: float, dist: float) -> bool:
        return abs(mid - val) < dist

    voltage = 3.3 * (detect_adc.read_u16() / 65535)
    return voltage

    if is_around(3.2, voltage, 0.1):
        return SensorState.Disconnected
    elif is_around(0.6, voltage, 0.1):
        return SensorState.LightIntensity

    return SensorState.Unknown


def read_sensor(num_samples: int = 1):
    async with sensor_lock:
        if not sensor_adc:
            return None
        acc = 0
        for _ in range(num_samples):
            acc += sensor_adc.read_u16()

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
