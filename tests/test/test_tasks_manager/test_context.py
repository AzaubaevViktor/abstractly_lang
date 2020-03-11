import asyncio
from asyncio import CancelledError

import pytest

from core.tasks_manager import TasksManager

pytestmark = pytest.mark.asyncio


async def _ok(x, sleep=0):
    await asyncio.sleep(sleep)
    return x


async def do_test(*chars):
    tasks = []
    with TasksManager() as manager:
        try:
            for char in chars:
                assert len(char) == 1
                tasks.append(manager.apply(_ok(ord(char)), char * 10))

            await manager.results()
        except CancelledError:
            print(manager.stats)
            for task_, info_ in manager.stats:
                task_: asyncio.Task
                assert not task_.done()

    return tasks


async def test_context(capsys):
    captured = capsys.readouterr()
    task: asyncio.Task = asyncio.create_task(do_test("a", "b", "c"))

    task.cancel()

    try:
        await task
    except Exception as e:
        assert isinstance(e, CancelledError)

    for ch in ("a", "b", "c"):
        assert ch * 10 in captured.out

    result = task.result()

    for task in result:
        assert task.done()
        assert isinstance(task.exception(), CancelledError)
