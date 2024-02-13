import minipb


@minipb.process_message_fields
class GetReading(minipb.Message):
    num_samples = minipb.Field(1, minipb.TYPE_UINT32)


@minipb.process_message_fields
class ReadingResponse(minipb.Message):
    raw_reading = minipb.Field(1, minipb.TYPE_UINT32)
    scaled_reading = minipb.Field(2, minipb.TYPE_FLOAT)


@minipb.process_message_fields
class SetLed(minipb.Message):
    color = minipb.Field(1, minipb.TYPE_UINT32)


@minipb.process_message_fields
class SetSensorOptions(minipb.Message):
    zero_point = minipb.Field(1, minipb.TYPE_UINT32)
    avg_window = minipb.Field(2, minipb.TYPE_UINT32)
    scale = minipb.Field(3, minipb.TYPE_FLOAT)


@minipb.process_message_fields
class GradientMode(minipb.Message):
    left_color = minipb.Field(1, minipb.TYPE_UINT32)
    left_endpoint = minipb.Field(2, minipb.TYPE_FLOAT)

    right_color = minipb.Field(3, minipb.TYPE_UINT32)
    right_endpoint = minipb.Field(4, minipb.TYPE_FLOAT)


@minipb.process_message_fields
class FavPoint(minipb.Message):
    color = minipb.Field(1, minipb.TYPE_UINT32)
    point = minipb.Field(2, minipb.TYPE_FLOAT)


@minipb.process_message_fields
class FavPointsMode(minipb.Message):
    points = minipb.Field(1, FavPoint, repeated=True)
    gradient_width = minipb.Field(2, minipb.TYPE_FLOAT)


@minipb.process_message_fields
class AutoMode(minipb.Message):
    slot = minipb.Field(1, minipb.TYPE_UINT32)
    # oneof mode {
    mode_gradient = minipb.Field(2, GradientMode)
    mode_fav_points = minipb.Field(3, FavPointsMode)
    # }
    oneof_mode = (mode_gradient, mode_fav_points)


@minipb.process_message_fields
class SetAutoOptions(minipb.Message):
    # oneof activate {
    activate_mode = minipb.Field(1, AutoMode)
    activate_slotted_mode = minipb.Field(2, minipb.TYPE_UINT32)
    # }
    oneof_activate = (activate_mode, activate_slotted_mode)

    # https://protobuf.dev/programming-guides/encoding/#maps
    slot_modes = minipb.Field(3, AutoMode, repeated=True)


@minipb.process_message_fields
class SubscribeReading(minipb.Message):
    enable = minipb.Field(1, minipb.TYPE_BOOL)
    update_rate = minipb.Field(2, minipb.TYPE_UINT32)


@minipb.process_message_fields
class MainHostMsg(minipb.Message):
    # oneof content {
    set_led = minipb.Field(1, SetLed)
    get_reading = minipb.Field(2, GetReading)
    set_sensor_options = minipb.Field(3, SetSensorOptions)
    set_auto_options = minipb.Field(4, SetAutoOptions)
    subscribe_reading = minipb.Field(5, SubscribeReading)
    # }
    oneof_content = (set_led, get_reading, set_sensor_options, set_auto_options, subscribe_reading)


@minipb.process_message_fields
class MainNodeMsg(minipb.Message):
    is_subscription_response = minipb.Field(1, minipb.TYPE_BOOL)
    # oneof content {
    reading_response = minipb.Field(2, ReadingResponse)
    # }
    oneof_content = (reading_response, )


def extract_oneof_field(msg, oneof_list):
    extracted_msg = None
    msg_cnt = 0

    for possible_field in oneof_list:
        possible_msg = getattr(msg, possible_field.name)
        if possible_msg:
            msg_cnt += 1
            extracted_msg = possible_msg  # save last encountered msg

    if msg_cnt > 1:
        print(f"ERROR: oneof condition not satisfied for {type(msg).__name__} message:\n\t", msg)

    return extracted_msg
