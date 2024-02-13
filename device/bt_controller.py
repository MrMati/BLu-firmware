import sys

sys.path.append("")

from micropython import const
import uasyncio as asyncio
import aioble
import bluetooth

import mini_protos as mp
from hardware import init_hardware, free_hardware
from app_logic import host_msg_handler

_USER_DATA_UUID = bluetooth.UUID(0x181C)

_DATA_HOST_IN_UUID = bluetooth.UUID(0x2B30)
_DATA_HOST_OUT_UUID = bluetooth.UUID(0x2B31)

_ADV_APPEARANCE_CONTACT_SENSOR = const(0x0548)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = const(250_000)

# Register GATT server.
data_service = aioble.Service(_USER_DATA_UUID)
# char variables are named from current device perspective
data_out_char = aioble.Characteristic(
    data_service, _DATA_HOST_IN_UUID, read=True, notify=True
)
data_in_char = aioble.Characteristic(
    data_service, _DATA_HOST_OUT_UUID, write=True, notify=True
)
aioble.register_services(data_service)


async def control_task(conn):
    try:
        with conn.timeout(None):
            while True:
                print("Waiting for write")
                await data_in_char.written()
                data_in = data_in_char.read()
                print("Recv:", data_in)

                host_msg = mp.MainHostMsg.decode(data_in)
                node_msg = host_msg_handler(host_msg)

                if node_msg:
                    node_msg_enc = node_msg.encode()
                    data_out_char.write(node_msg_enc)
                    data_out_char.notify(conn)

    except aioble.DeviceDisconnectedError:
        return


async def peripheral_task():
    while True:
        async with await aioble.advertise(
                _ADV_INTERVAL_MS,
                name="BLu",
                services=[_USER_DATA_UUID],
                appearance=_ADV_APPEARANCE_CONTACT_SENSOR,
        ) as connection:
            print("Connection from", connection.device)

            # c_task = asyncio.create_task(control_task())
            await control_task(connection)

            await connection.disconnected()
            print("Device disconnected")
            # Allegedly prevents a delayed crash of `await connection.disconnected()`
            # while connection.is_connected() == True:
            #    #print(f'Connection status: {connection.is_connected()}')
            #    await asyncio.sleep_ms(1000)


async def main():
    init_hardware()

    t2 = asyncio.create_task(peripheral_task())
    await asyncio.gather(t2)

    # Not expected to ever get here, as of now
    free_hardware()


asyncio.run(main())
