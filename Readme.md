# Abstractly 
Язык программирования, в котором можно менять правила разбора прямо во время работы.

## Что работает на данный момент
* Арифметические операции  
  Числа, +-/*, **, факториал (!)
* Большой выбор парсеров (python)
  * `EmptyParser`
  * `CharParser`
  * `CharParser.line`
  * `OrParser` (с поддержкой лево-рекурсивных правил!)  
  * `AndParser`
  * `RepeatParser`
  * `FunParser` + `KeyArgument`
  * `EndLineParser`
  * `PriorityParser`
* Создание парсеров из оболочки
  * `EmptyParser`
  * `CharParser`
  * `OrParser`
* Работа с переменными
  * Получение значения
  * Присваивание


## TODO
* Дописать генераторы всех парсеров
* Более грамотно переписать работу с переменными и контекстами
* Работа с файлами
* Красивое избавление от рекурсии (как в OrParser и MultiParser)
* Красивое отображение ошибок
* Переписать всё с нуля, так как сейчас код скорее набор костылей

## Левая рекурсия
```python
from typing import List
from line import Line
from parser import CharParser, OrParser
from parser import ParseVariant
x = OrParser(CharParser('x'))
x |= x & CharParser('y')

results: List[ParseVariant] = list(x.parse(Line('xyy')))

assert results == [ 
    ParseVariant(CharParser('x'), Line('yy')),
    ParseVariant(CharParser('x') & CharParser('y'), Line('y')),
    ParseVariant(CharParser('x') & CharParser('y') & CharParser('y'), Line(''))
]
```

Основная проблема с леворекурсивными правилами -- парсер наподобие OrParser зацикливается.  

Алгоритм работы для `OrParser`:
* Проверяется, есть ли для текущей пары *parser ~ line* варианты разбора
  * Если есть, они возвращаются
* Если парсер в данном контексте вызывается второй раз, закончить работу
* Повторять:
  * Распарсить line
  * Если есть новые варианты разбора -- вернуть их и записать
  * Старые не возвращать
  * Если новых вариантов разбора нет, закончить работу
 
Таким образом удалось победить левую рекурсию.

## Приоритеты
Для того, чтобы не приходилось писать монструозных конструкций, решено было использовать `PriorityParser`, 
который проверяет, есть ли в дочерних парсерах значения меньше (или больше -- зависит от реализации)
текущего и, если они есть, не считает этот вариант разбора неправильным. Таким образом мы можем задать такие правила:
```
.=> @ |= (a:@ + b:@ => a + b)#10
.=> @ |= (a:@ * b:@ => a * b)#20
.=> 1 + 2 * 3
7
``` 
За счёт того, что вариант разбора
```
.----20---.
.--10-.
(1 + 2) * 3
```
Будет неверным, так как внутри парсера с приоритом 20 будет 
парсер с приоритетом 10.  
В то же время вариант
```
.---10----.
    .--20-.
1 + (2 * 3)
```
Будет верным, так как значение приоритета возрастает при продвижении
в глубину.

## ПРАВИЛА
Как известно, все правила написаны кровью, потом и сорванными дедлайнами.  
Для того, чтобы сделать продукт в кратчайшие сроки, нужно придерживаться следующих правил:

* Писать как можно больше тестов
  * 👍 Использовать [TDD](https://en.wikipedia.org/wiki/Test-driven_development)
* Понятность кода > Скорость кода
  * 👍 НИКАКИХ преждевременных оптимизаций
* Инкапсуляция > Скорость кода
  * 👍 Чем меньше code cohesion -- тем лучше
* Простота > всего


## Как?
* Строка приходит в исполнитель
* Исполнитель преобразует строку с помощью парсеров в AST
    * Parser превращает строку в:
      List[возможное AST, оставшаяся строка]
* AST представляет собой граф, у которого:
    * Каждая нода -- часть строки с мета-информацией
    * Мета-информация:
        * Тип парсера
        * Функция, которая выполняется
* AST начинает выполняться, начиная с листьев
    * Функция, которая лежит в парсере, имеет доступ к:
        * Строке в парсере
        * Детишкам
    * Функция выполняется, возвращает значение
    * Когда всё AST выполнилось, мы возвращаем значение из корня
    

### Парсеры
#### Пустой парсер
```
line ==> [<∅, line>]
```
#### Парсер символа
```
✓ line ==> [<`ch`, line[1:]>]  
🚫line ==> [<∅, line>]  
```
#### A & B
```
AY     =A> [<`A_1`, Y>, ..., <`A_k`, Y>]   
BY     =B> [<`B_1`, Y>, ..., <`B_n`, Y>]   

✓ ABC  ==> [<(`A_1` & `B_1`), C>, ..., <(`A_k` & `B_n`), C>]   
🚫AXC  ==> [<∅, AXC>]   
```
#### A | B
```
XZ =A> [<`A_1`, Z>, ..., <`A_k`, Z>]   
XZ =B> [<`B_1`, Z>, ..., <`B_n`, Z>]   
XZ ==> [<`A_1`, Z>, ..., <`A_k`, Z>, <`B_1`, Z>, ..., <`B_n`, Z>]   
```
#### A repeat from x to y
```
X =A=> [⍺, β, ...]
 x     y
X           => [<∅, XXXX>]
XXX         => [<⍺⍺, X>, <⍺β, X>, ..., <ββ, X>, <⍺⍺⍺, ∅>, ..., <βββ, ∅>]
```
#### A?; A+; A*
* `A?`: A repeat from 0 to 1
* `A+`: A repeat from 1 to inf
* `A*`: A repeat from 0 to inf

#### Parser A with Function F
```
XZ =A> [<`A_1`, Z>, ..., <`A_k`, Z>] 
XZ ==> [<`A_1`:F, Z>, ..., <`A_k`:F, Z>]
```