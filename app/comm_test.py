import asyncio
import logging
import contextlib
import time

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.uuids import normalize_uuid_16, register_uuids

from protos.main_host_pb2 import *
from protos.auto_modes_pb2 import *
from protos.containers_pb2 import *
from protos.manual_pb2 import *


logger = logging.getLogger(__name__)

response_received = asyncio.Event()

data_in_uuid = normalize_uuid_16(0x2B30)
data_out_uuid = normalize_uuid_16(0x2B31)
register_uuids({data_in_uuid: "DATA_HOST_IN",
                data_out_uuid: "DATA_HOST_OUT"})


def encode_host_msg():
    if True:
        set_led = SetLed()
        set_led.color = 0xffff
        host_msg = MainHostMsg(set_led=set_led)
        return host_msg.SerializeToString()
    else:
        get_reading = GetReading(num_samples=1)
        host_msg = MainHostMsg(get_reading=get_reading)
        return host_msg.SerializeToString()


def decode_node_msg(data: bytes):
    node_msg = MainNodeMsg()
    node_msg.ParseFromString(data)
    main_msg = getattr(node_msg, node_msg.WhichOneof('content'))
    return main_msg


def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    """Simple notification handler which prints the data received."""
    logger.info("%s: %r", characteristic.description, decode_node_msg(bytes(data)))
    response_received.set()


async def main(address):
    device = await BleakScanner.find_device_by_address(address)
    if device is None:
        logger.error("could not find device with address '%s'", address)
        return

    logger.info("connecting to device...")

    async with BleakClient(device) as client:
        logger.info("connected")

        await client.start_notify(data_in_uuid, notification_handler)
        data = encode_host_msg()
        for _ in range(1):
            await client.write_gatt_char(data_out_uuid, bytearray(data), response=True)
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(response_received.wait(), 1)
            response_received.clear()
            time.sleep(1)
        # await client.stop_notify(data_in_uuid)

        logger.info("disconnecting...")

    logger.info("disconnected")


debug = False
address = "D8:3A:DD:2E:56:BB"

if __name__ == "__main__":
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main(address))
