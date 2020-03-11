import pytest

from core.tasks_manager import TasksManager


@pytest.fixture(scope='function')
async def manager():
    manager = TasksManager(name="test")

    yield manager

    await manager.cancel()
