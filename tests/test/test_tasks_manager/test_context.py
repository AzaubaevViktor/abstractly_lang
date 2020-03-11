import asyncio
from asyncio import CancelledError

import pytest

from core.tasks_manager import TasksManager

pytestmark = pytest.mark.asyncio


async def _ok(x, sleep=0):
    await asyncio.sleep(sleep)
    return x


async def do_test(ev, *chars):
    tasks = []
    async with TasksManager() as manager:
        try:
            for char in chars:
                assert len(char) == 1
                tasks.append(manager.apply(_ok(ord(char), ord(char)), char * 10))
            ev.set()
            await manager.results()
        except CancelledError:
            print(manager.stats)
            for task_, info_ in manager.stats:
                task_: asyncio.Task
                assert not task_.done() or task_.cancelled()

    return tasks


async def test_context(capsys):
    ev = asyncio.Event()
    task: asyncio.Task = asyncio.create_task(do_test(ev, "a", "b", "c"))

    await ev.wait()

    await asyncio.sleep(1)

    task.cancel()

    await task

    captured = capsys.readouterr()

    for ch in ("a", "b", "c"):
        assert ch * 10 in captured.out

    result = task.result()

    for task in result:
        assert task.done()
        assert task.cancelled()
