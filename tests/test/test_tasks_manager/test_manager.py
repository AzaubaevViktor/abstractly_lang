import asyncio
from typing import Optional, List

import pytest

from core.tasks_manager import TasksManager, WrappedCancelledError

pytestmark = pytest.mark.asyncio


async def test_aio():
    assert True


async def _ok(x, event: Optional[asyncio.Event] = None):
    if event:
        await event.wait()
    return x


async def test_simple(manager):
    manager.run(_ok(100), _ok(120), _ok(140))

    results = await manager.results()

    assert set(results) == {100, 120, 140}


async def test_run_multiple(manager):
    manager.run(_ok(100), _ok(200))

    manager.run(_ok(300), _ok(400))

    result = await manager.results()

    assert set(result) == {100, 200, 300, 400}


async def test_pop(manager):
    ev = asyncio.Event()

    manager.run(_ok(100), _ok(200, ev))

    assert 100 == await manager.pop()

    ev.set()

    assert 200 == await manager.pop()


def _count_waited_stats(manager):
    waited = 0

    for task_, info_ in manager.stats:
        task_: asyncio.Task
        if not task_.done():
            waited += 1

    return waited


async def test_stats(manager):
    ev = asyncio.Event()

    manager.run(_ok(100), _ok(200, ev))

    assert len(manager.stats) == 2

    for task_, info_ in manager.stats:
        assert isinstance(task_, asyncio.Task)
        assert info_ is None

    while _count_waited_stats(manager) == 0:
        await asyncio.sleep(0.1)

    assert _count_waited_stats(manager) == 1

    ev.set()

    while _count_waited_stats(manager) == 1:
        await asyncio.sleep(0.1)

    assert _count_waited_stats(manager) == 2


async def test_pop_stats(manager):
    manager.run(*(_ok(x) for x in range(5)))

    results = []

    while len(manager.stats):
        prev = len(manager.stats)
        results.append(await manager.pop)
        assert prev - 1 == len(manager.stats)

    assert set(results) == set(range(5))

    assert len(manager.stats) == 0


async def test_stats_info(manager):
    assert isinstance(manager.apply(_ok(1), "one"), asyncio.Task)
    assert isinstance(manager.apply(_ok(2), "two"), asyncio.Task)

    infos = [info for task_, info in manager.stats]

    assert set(infos) == {"one", "two"}


async def test_clean(manager):
    ev = asyncio.Event()
    manager.run(_ok(10), _ok(20), _ok(30, ev))

    while len(manager.stats) > 1:
        manager.clean()

    ev.set()

    while len(manager.stats) > 0:
        manager.clean()

    assert not manager.stats


async def test_cancel(manager):
    ev = asyncio.Event()
    manager.run(_ok(10), _ok(20, ev))

    while True:
        task_done = None
        for task_, info_ in manager.stats:
            if task_.done():
                task_done = task_
                break

        if task_done:
            assert task_done.done()
            break

    tasks: List[asyncio.Task] = [task_ for task_, info_ in manager.stats]

    await manager.cancel()

    for task_ in tasks:
        assert task_.done()

    assert tasks[0].result() == 10
    assert isinstance(tasks[1].exception(), WrappedCancelledError)


async def _calc(x):
    return 1 / x


async def test_exc(manager):
    manager.run(_calc(0), _calc(1), _calc(2))

    tasks = [task_ for task_, _info_ in manager.stats]

    with pytest.raises(ZeroDivisionError):
        manager.results()


async def test_exc_ret(manager):
    manager.run(_calc(0), _calc(1), _calc(2))

    tasks = [task_ for task_, _info_ in manager.stats]

    results = manager.results(return_exceptions=True)

    assert len(results) == 3

    for result in results[:]:
        if isinstance(result, Exception):
            results.remove(result)
            break

    assert len(results) == 2

    assert set(results) == {1 / 1, 1 / 2}


