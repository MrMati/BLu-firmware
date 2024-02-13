import sys
sys.path.append("../device")

from device.mini_protos import extract_oneof_field

import device.mini_protos as mp
from app.protos.main_host_pb2 import *
from app.protos.auto_modes_pb2 import *


def printd(*args):
    print(*args, end='\n' + '-' * 20 + '\n')


def test1():
    sensor_options = SetSensorOptions(zero_point=1234)
    encoded_sensor_opt = SetSensorOptions.SerializeToString(sensor_options)

    decoded_sensor_opt = mp.SetSensorOptions.decode(encoded_sensor_opt)
    printd(sensor_options, decoded_sensor_opt)


def test2():
    auto_opts = SetAutoOptions()
    auto_opts.activate_slotted_mode = 1
    fav_mode = FavPointsMode(points=[FavPoint(color=0xFF00FFFF, point=0.375)], gradient_width=20.5)
    auto_opts.slot_modes.append(AutoMode(mode_fav_points=fav_mode))
    encoded_auto_opts = SetAutoOptions.SerializeToString(auto_opts)

    decoded_auto_opts = mp.SetAutoOptions.decode(encoded_auto_opts)
    printd(auto_opts, decoded_auto_opts)


def test3():
    fav_mode = mp.FavPointsMode(points=(mp.FavPoint(color=0xFF00FFFF, point=0.375),), gradient_width=20.5)
    auto_opts = mp.SetAutoOptions(activate_slotted_mode=1, slot_modes=(mp.AutoMode(mode_fav_points=fav_mode),))
    encoded_auto_opts = auto_opts.encode()

    decoded_auto_opts = SetAutoOptions()
    decoded_auto_opts.ParseFromString(encoded_auto_opts)
    printd(auto_opts, '\n', decoded_auto_opts)


def test4():
    fav_mode = mp.FavPointsMode(points=(mp.FavPoint(color=0xFF00FFFF, point=0.375),), gradient_width=20.5)
    grad_mode = mp.GradientMode(left_endpoint=-1.0, left_color=0xFF, right_endpoint=1.0, right_color=0xFF00)
    auto_opts = mp.SetAutoOptions(slot_modes=(mp.AutoMode(mode_fav_points=fav_mode, mode_gradient=grad_mode),))
    encoded_auto_opts = auto_opts.encode()

    decoded_auto_opts = SetAutoOptions()
    decoded_auto_opts.ParseFromString(encoded_auto_opts)
    printd(auto_opts, '\n', decoded_auto_opts)


def test5():
    fav_mode = mp.FavPointsMode(points=(mp.FavPoint(color=0xFF00FFFF, point=0.375),), gradient_width=20.5)
    grad_mode = mp.GradientMode(left_endpoint=-1.0, left_color=0xFF, right_endpoint=1.0, right_color=0xFF00)
    auto_opts = mp.SetAutoOptions(slot_modes=[mp.AutoMode(mode_fav_points=fav_mode)])  # , mode_gradient=grad_mode
    encoded_auto_opts = auto_opts.encode()

    decoded_auto_opts = mp.SetAutoOptions.decode(encoded_auto_opts)
    print(decoded_auto_opts)
    # TODO: oneof checking for mode_fav_points and mode_gradient pair


def test6():
    set_led = mp.SetLed(rgba=0x10FF)
    get_reading = mp.GetReading(num_samples=10)
    host_msg = mp.MainHostMsg(set_led=set_led, get_reading=get_reading)
    print(host_msg)

    extracted_msg = extract_oneof_field(host_msg, host_msg.oneof_content)

    print("Extracted msg:", extracted_msg)


# test1()
# test2()
# test3()
test4()
# test5()
# test6()
