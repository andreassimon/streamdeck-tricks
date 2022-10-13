import asyncio
import aioconsole
import sys
import threading


async def ainput():
    loop = asyncio.get_event_loop()
    fut = loop.create_future()

    def _run():
        line = sys.stdin.read()
        loop.call_soon_threadsafe(fut.set_result, line)

    threading.Thread(target=_run, daemon=True).start()
    return await fut


async def console_input_loop():
    while True:
        inp = await ainput()
        print(f"[{inp.strip()}]")


async def sleeper():
    await asyncio.sleep(10)
    print("stop")
    loop.stop()


async def console_keys():
    while True:
        response = await aioconsole.ainput('Is this your line? ')
        print("response was", response)


loop = asyncio.get_event_loop()
# loop.create_task(console_input_loop())
loop.create_task(sleeper())
loop.create_task(console_keys())
loop.run_forever()
