# Config Translator

## Что делает этот проект?

Это транслятор конфигурационных файлов, который:

1. Читает файлы специального формата с расширением `.txt`
2. Поддерживает следующие возможности:
   - Объявление и использование переменных
   - Работа с числовыми массивами
   - Комментарии (однострочные и многострочные)
   - Вычисление выражений (например, `[x + 1]` или `[max(1,2,3)]`)
   - Вычисление константных выражений на этапе трансляции (например, `.[x + 1]`)
3. Преобразует эти файлы в формат TOML

### Пример работы:

**Входной файл (input.txt):**
```
! Настройки игры
var player_speed = 5;
var initial_lives = 3;
var bonus_points = { 10, 20, 30 };
.[player_speed + 1]  ! Вычисляет скорость на этапе трансляции
```

**Выходной файл (output.toml):**
```toml
player_speed = 5.0
initial_lives = 3.0
bonus_points = [10.0, 20.0, 30.0]
expression_result = 6.0
```

### Для чего это нужно?

1. **Упрощение конфигурации:** Вместо прямого редактирования TOML файлов, пользователи могут использовать более простой и понятный формат
2. **Динамические значения:** Возможность вычислять значения на основе других параметров
3. **Проверка корректности:** Транслятор проверяет синтаксис и выдаёт понятные ошибки
4. **Документирование:** Поддержка комментариев помогает документировать настройки

## Общее описание
Config Translator - это инструмент для парсинга конфигурационных файлов специального формата и преобразования их в TOML формат. Поддерживает переменные, массивы, комментарии и вычисление выражений.

## Описание функций и настроек

### Класс ConfigParser

#### Методы:
1. `__init__(self)`
   - Инициализация парсера
   - Создает пустой словарь для переменных
   - Инициализирует счетчик текущей строки
   - Инициализирует список строк файла

2. `parse_file(self, filename)`
   - Входные параметры:
     - filename (str): путь к файлу конфигурации
   - Читает файл конфигурации
   - Возвращает результат парсинга
   - Обрабатывает ошибку FileNotFoundError

3. `parse(self)`
   - Основной метод парсинга
   - Обрабатывает каждую строку файла
   - Возвращает словарь с результатами вычислений

4. `skip_multiline_comment(self)`
   - Пропускает многострочный комментарий
   - Выбрасывает SyntaxError если комментарий не закрыт

5. `parse_variable(self, line)`
   - Входные параметры:
     - line (str): строка с объявлением переменной
   - Парсит объявление переменной
   - Поддерживает числа и массивы
   - Выбрасывает SyntaxError при некорректном синтаксисе

6. `parse_array(self, array_str)`
   - Входные параметры:
     - array_str (str): строка с объявлением массива
   - Парсит объявление массива
   - Поддерживает только числовые элементы
   - Выбрасывает SyntaxError при некорректном синтаксисе

7. `evaluate_expression(self, expr)`
   - Входные параметры:
     - expr (str): строка с выражением
   - Вычисляет значение выражения
   - Поддерживает операции: +, -, *, /
   - Поддерживает функцию max()
   - Заменяет переменные их значениями

### Поддерживаемые конструкции языка:

1. **Объявление переменных**
   ```
   var имя = значение;
   ```
   - имя: должно начинаться с буквы, может содержать буквы и цифры
   - значение: число с плавающей точкой или массив

2. **Объявление массивов**
   ```
   var имя = { элемент1, элемент2, ... };
   ```
   - элементы: только числа с плавающей точкой
   - разделитель: запятая
   - пустой массив: `{ }`

3. **Комментарии**
   - Однострочные:
     ```
     ! Это комментарий
     ```
   - Многострочные:
     ```
     =begin
     Это многострочный
     комментарий
     =end
     ```

4. **Выражения**
   - Обычные выражения:
     ```
     [выражение]
     ```
   - Константные выражения (вычисляются на этапе трансляции):
     ```
     .[выражение]
     ```
   - Поддерживаемые операции:
     - Сложение: `+`
     - Вычитание: `-`
     - Умножение: `*`
     - Деление: `/`
   - Поддерживаемые функции:
     - `max(число1, число2, ...)`: возвращает максимальное из чисел

### Обработка ошибок

1. **SyntaxError**
   - Некорректное объявление переменной
   - Некорректный формат массива
   - Некорректные элементы массива
   - Незакрытый многострочный комментарий
   - Некорректное выражение

2. **FileNotFoundError**
   - Файл конфигурации не найден

### Параметры командной строки

```bash
python config_translator.py input_file.txt output.toml
```

- `input_file.txt`: входной файл конфигурации
- `output.toml`: выходной TOML файл (опционально)

## Сборка проекта

1. Установка зависимостей:
```bash
pip install -r requirements.txt
```

2. Запуск тестов:
```bash
pytest test_config_translator.py
```

3. Использование транслятора:
```bash
python config_translator.py input_file.txt output.toml
```

## Примеры использования

### Пример 1: Конфигурация игры
```
! Настройки игры
var player_speed = 5;
var initial_lives = 3;
var bonus_points = { 10, 20, 30 };
.[player_speed + 1]  ! Вычисляет скорость на этапе трансляции
```

### Пример 2: Настройки сервера
```
=begin
Конфигурация сервера
Версия 1.0
=end
var port = 8080;
var max_connections = 100;
[max(port, max_connections)]
```

## Результаты тестов

Все тесты успешно пройдены:
- test_comments: ✓
- test_arrays: ✓
- test_expressions: ✓
- test_max_function: ✓
- test_syntax_error: ✓
- test_unclosed_comment: ✓
- test_constant_expression: ✓