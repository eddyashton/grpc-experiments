from collections import deque
import random
import asyncio
import datetime



class RunSome:
    def __init__(self):
        self.running = set()
        self.waiting = deque()

    @property
    def running_task_count(self):
        return len(self.running)

    def add_task(self, coro):
        self._start_task(coro)

    def _start_task(self, coro):
        self.running.add(coro)
        asyncio.create_task(self._task(coro))

    async def _task(self, coro):
        try:
            return await coro
        finally:
            self.running.remove(coro)
            if self.waiting:
                coro2 = self.waiting.popleft()
                self._start_task(coro2)


async def main():
    runner = RunSome()

    async def rand_delay():
        rnd = random.random() + 0.5
        now = datetime.datetime.utcnow().isoformat()
        print(
            f"{now} | Task started | {asyncio.current_task().get_name():>10s} | {runner.running_task_count}"
        )
        await asyncio.sleep(rnd)
        now = datetime.datetime.utcnow().isoformat()
        print(
            f"{now} | Task ended   | {asyncio.current_task().get_name():>10s} | {runner.running_task_count}"
        )

    for _ in range(50):
        runner.add_task(rand_delay())
    # keep the program alive until all the tasks are done
    while runner.running_task_count > 0:
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
