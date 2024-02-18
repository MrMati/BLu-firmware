import sys

sys.path.append("")

from micropython import const
import bluetooth
import asyncio
import aioble

import mini_protos as mp
from app_logic import host_msg_handler
from app_state import app_state

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


async def data_out_task(conn):
    try:
        with conn.timeout(None):
            while True:
                response = await app_state.response_queue.get()
                print(f"{response=}")
                data_out_char.write(response)
                data_out_char.notify(conn)

    except aioble.DeviceDisconnectedError:
        return


async def data_in_task(conn):
    try:
        with conn.timeout(None):
            while True:
                print("Waiting for write")
                await data_in_char.written()
                data_in = data_in_char.read()
                print(f"{data_in=}")

                host_msg = mp.MainHostMsg.decode(data_in)
                node_msg = host_msg_handler(host_msg)

                if node_msg:
                    node_msg_enc = node_msg.encode()
                    await app_state.response_queue.put(node_msg_enc)

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

            c_task = asyncio.create_task(data_in_task(connection))
            r_task = asyncio.create_task(data_out_task(connection))
            await asyncio.gather(c_task, r_task)

            await connection.disconnected()

            # TODO: extract disconnection cleanup to function
            app_state.sensor_sub_enabled.clear()
            app_state.response_queue.empty()

            print("Device disconnected")
            # Allegedly prevents a delayed crash of `await connection.disconnected()`
            # while connection.is_connected() == True:
            #    #print(f'Connection status: {connection.is_connected()}')
            #    await asyncio.sleep_ms(1000)
