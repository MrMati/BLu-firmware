import mini_protos as mp


def test6():
    set_led = mp.SetLed(rgba=0x10FF)
    get_reading = mp.GetReading(num_samples=10)
    host_msg = mp.MainHostMsg(set_led=set_led, get_reading=get_reading)
    print(host_msg)

    extracted_msg = mp.extract_oneof_field(host_msg, host_msg.oneof_content)

    print("Extracted msg:", extracted_msg)


test6()