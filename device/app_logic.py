from math import floor

import asyncio
import mini_protos as mp
from hardware import set_led, read_sensor
from app_state import app_state


# Contains most of the application logic
# Independent of micropython, so it can be run on host with mocked hardware interface


async def host_msg_handler(host_msg: mp.MainHostMsg):
    main_msg = mp.extract_oneof_field(host_msg, host_msg.oneof_content)
    if not main_msg:
        return
    resp_msg = await msg_handlers[type(main_msg)](main_msg)

    if resp_msg:
        if type(resp_msg) is mp.ReadingResponse:
            node_msg = mp.MainNodeMsg(reading_response=resp_msg)
        else:
            print("ERROR: Some msg_handler responded with unexpected response type:", type(resp_msg).__name__)
            return None
        return node_msg


async def set_led_handler(msg: mp.SetLed):
    print("Setting led to color:", hex(msg.color))
    set_led(msg.color)


# Independent of window avg
async def get_reading_handler(msg: mp.GetReading):
    print("Host requested a sensor reading, we probably should do something about it")
    if msg.num_samples > 1:
        print(f"Oh. And it wants avg from {msg.num_samples} samples")

    value = read_sensor(msg.num_samples or 1)

    scaled_value = scale_sensor_reading(value)

    resp_msg = mp.ReadingResponse(raw_reading=floor(value), scaled_reading=scaled_value)
    return resp_msg


async def set_sensor_options_handler(msg: mp.SensorOptions):
    app_state.scaling_factor = msg.scale
    app_state.set_avg_window_size(msg.avg_window)
    app_state.zero_point = msg.zero_point


async def set_auto_options_handler(msg: mp.AutoOptions):
    raise NotImplementedError


async def subscribe_reading_handler(msg: mp.SubscribeReading):
    if msg.enable:
        app_state.sensor_sub_enabled.set()
        app_state.sensor_sub_update_rate = msg.update_rate
    else:
        app_state.sensor_sub_enabled.clear()


msg_handlers = {
    mp.SetLed: set_led_handler,
    mp.GetReading: get_reading_handler,
    mp.SensorOptions: set_sensor_options_handler,
    mp.AutoOptions: set_auto_options_handler,
    mp.SubscribeReading: subscribe_reading_handler,
}


def scale_sensor_reading(val: float) -> float:
    return (val - app_state.zero_point) * app_state.scaling_factor


async def subscriptions_task():
    while True:
        await app_state.sensor_sub_enabled.wait()
        await asyncio.sleep(1 / app_state.sensor_sub_update_rate)

        value = read_sensor(1)  # TODO: avg window

        scaled_value = scale_sensor_reading(value)
        sub_resp_msg = mp.ReadingResponse(raw_reading=floor(value), scaled_reading=scaled_value)
        node_msg = mp.MainNodeMsg(reading_response=sub_resp_msg, is_subscription_response=True)
        await app_state.response_queue.put(node_msg.encode())
