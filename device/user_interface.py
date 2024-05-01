import asyncio
from hardware import perform_detection, read_sensor, button_event
import core1


async def ui_task():
    try:
        core1.launch()
        pass
    except RuntimeError:
        pass

    await asyncio.sleep(3)

    core1.set_view(1)
    core1.set_slot(slot := 0)

    while True:
        button_num = await button_event.wait()
        if button_num == 0:
            slot += 1
        elif button_num == 1:
            slot -= 1

        slot = min(max(slot, 0), 2)
        core1.set_slot(slot)
