import argparse
import re
import sys
import tomli_w

class ConfigParser:
    def __init__(self):
        self.variables = {}
        self.current_line = 0
        self.lines = []

    def parse_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.lines = f.readlines()
            return self.parse()
        except FileNotFoundError:
            print(f"Ошибка: Файл {filename} не найден", file=sys.stderr)
            sys.exit(1)

    def parse(self):
        result = {}
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line].strip()
            
            # Пропуск пустых строк
            if not line:
                self.current_line += 1
                continue
            
            # Обработка однострочных комментариев
            if line.startswith('!'):
                self.current_line += 1
                continue
            
            # Обработка многострочных комментариев
            if line == '=begin':
                self.skip_multiline_comment()
                continue
            
            # Обработка объявления переменных
            if line.startswith('var'):
                self.parse_variable(line)
                self.current_line += 1
                continue
            
            # Обработка выражений в квадратных скобках
            if line.startswith('[') or line.startswith('.['):
                is_constant = line.startswith('.[')
                expr = line[2:-1].strip() if is_constant else line[1:-1].strip()
                value = self.evaluate_expression(expr)
                result['expression_result'] = value
                self.current_line += 1
                continue

            self.current_line += 1
            
        return result

    def skip_multiline_comment(self):
        self.current_line += 1
        while self.current_line < len(self.lines):
            if self.lines[self.current_line].strip() == '=end':
                self.current_line += 1
                return
            self.current_line += 1
        raise SyntaxError("Незакрытый многострочный комментарий")

    def parse_variable(self, line):
        match = re.match(r'var\s+([a-zA-Z][a-zA-Z0-9]*)\s*=\s*(.+);', line)
        if not match:
            raise SyntaxError(f"Некорректное объявление переменной в строке {self.current_line + 1}")
        
        name, value = match.groups()
        value = value.rstrip(';').strip()
        if value.startswith('{'):
            self.variables[name] = self.parse_array(value)
        else:
            try:
                self.variables[name] = float(value)
            except ValueError:
                raise SyntaxError(f"Некорректное значение в строке {self.current_line + 1}")

    def parse_array(self, array_str):
        if not (array_str.startswith('{') and array_str.endswith('}')):
            raise SyntaxError(f"Некорректный формат массива в строке {self.current_line + 1}")
        
        content = array_str[1:-1].strip()
        if not content:
            return []
        
        elements = []
        for item in content.split(','):
            item = item.strip()
            try:
                elements.append(float(item))
            except ValueError:
                raise SyntaxError(f"Некорректный элемент массива в строке {self.current_line + 1}")
        
        return elements

    def evaluate_expression(self, expr):
        # Замена переменных их значениями
        for var_name, var_value in self.variables.items():
            if isinstance(var_value, list):
                continue
            expr = expr.replace(var_name, str(var_value))
        
        # Обработка функции max
        if 'max(' in expr:
            match = re.search(r'max\((.*?)\)', expr)
            if match:
                args_str = match.group(1)
                args = []
                for arg in args_str.split(','):
                    arg = arg.strip()
                    if arg in self.variables:
                        if isinstance(self.variables[arg], list):
                            args.extend(self.variables[arg])
                        else:
                            args.append(self.variables[arg])
                    else:
                        try:
                            args.append(float(arg))
                        except ValueError:
                            raise SyntaxError(f"Некорректный аргумент в функции max в строке {self.current_line + 1}")
                return max(args)
        
        # Вычисление простых арифметических выражений
        try:
            return float(eval(expr, {"__builtins__": None}, {}))
        except:
            raise SyntaxError(f"Некорректное выражение в строке {self.current_line + 1}")

def main():
    parser = argparse.ArgumentParser(description='Конвертер конфигурационного языка в TOML')
    parser.add_argument('--input', required=True, help='Путь к входному файлу')
    args = parser.parse_args()

    config_parser = ConfigParser()
    result = config_parser.parse_file(args.input)
    
    # Вывод результата в TOML формате
    print(tomli_w.dumps(result))

if __name__ == '__main__':
    main()
