from test.test import TestedService
from tests.test.at_project.calc.service import Calculator


class TestCalculator(TestedService):
    async def test_calc(self):
        result = await Calculator.calc(a=1, b=2)
        assert 3 == result, result
