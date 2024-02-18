import asyncio

from bt_controller import peripheral_task
from app_logic import subscriptions_task
from hardware import init_hardware, free_hardware


async def main():
    init_hardware()

    t1 = asyncio.create_task(peripheral_task())
    t2 = asyncio.create_task(subscriptions_task())
    await asyncio.gather(t1, t2)

    # Not expected to ever get here, as of now
    free_hardware()


asyncio.run(main())
