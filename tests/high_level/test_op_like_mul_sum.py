import pytest

lines = """
number := ds:(0..9)+ => @to_int ds # Автоматически прокинет аргумент

mul_div := number
mul_div |= a:number __ '***' __ b:mul_div => @mul(a, b)
mul_div |= a:number __ '///' __ b:mul_div => @div(a, b)

add_sub := mul_div  
add_sub |= a:mul_div __ '+++' __ b:add_sub => @sum(a, b)
add_sub |= a:mul_div __ '---' __ b:add_sub => @diff(a, b)

expr |= add_sub  # Бам! Добавили в язык новую конструкцию
"""


@pytest.fixture(scope="function")
def aa(a):
    for line in lines.split("\n"):
        a(line)

    return a


@pytest.mark.parametrize("line, result", (
    ("1 +++ 2", 3),
    ("2 *** 3", 6),
    ("4 /// 2", 2.0),
    ("2 +++ 3 *** 4", 14)
))
def test_combine(aa, line, result):
    assert aa(line) == result
