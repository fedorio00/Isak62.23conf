import argparse
import re
import sys
import tomli_w
import os

class ConfigParser:
    def __init__(self):
        self.variables = {}
        self.current_line = 0
        self.lines = []

    def parse_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.lines = [line.strip() for line in f.readlines()]
            return self.parse()
        except FileNotFoundError:
            sys.exit(1)

    def parse(self):
        result = {}
        in_multiline_comment = False
        
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line].strip()
            
            # Пропускаем пустые строки
            if not line:
                self.current_line += 1
                continue
            
            # Обработка начала многострочного комментария
            if line == '=begin':
                in_multiline_comment = True
                self.current_line += 1
                continue
            
            # Обработка конца многострочного комментария
            if line == '=end':
                in_multiline_comment = False
                self.current_line += 1
                continue
            
            # Пропускаем строки внутри многострочного комментария
            if in_multiline_comment:
                self.current_line += 1
                continue
            
            # Пропускаем однострочные комментарии
            if line.startswith('!'):
                self.current_line += 1
                continue
            
            # Обработка объявления переменных
            if line.startswith('var'):
                self.parse_variable(line)
                self.current_line += 1
                continue
            
            # Обработка выражений
            if line.startswith('[') or line.startswith('.['):
                expr = line.strip('.[').strip(']').strip()
                try:
                    value = self.evaluate_expression(expr)
                    result['expression_result'] = float(value)
                except Exception:
                    pass
                self.current_line += 1
                continue
            
            # Если строка не подходит ни под один формат
            self.current_line += 1

        if in_multiline_comment:
            raise SyntaxError("Незакрытый многострочный комментарий")
            
        return result

    def parse_variable(self, line):
        match = re.match(r'var\s+(\w+)\s*=\s*(.+)', line)
        if not match:
            raise SyntaxError(f"Некорректное объявление переменной в строке {self.current_line + 1}")
        
        name, value = match.groups()
        value = value.strip().rstrip(';').strip()
        
        try:
            if value.startswith('{') and value.endswith('}'):
                self.variables[name] = self.parse_array(value)
            else:
                try:
                    if '.' in value:
                        self.variables[name] = float(value)
                    else:
                        self.variables[name] = int(value)
                except ValueError:
                    if value.startswith('"') and value.endswith('"'):
                        self.variables[name] = value[1:-1]
                    else:
                        raise SyntaxError(f"Некорректное значение в строке {self.current_line + 1}")
        except Exception as e:
            raise SyntaxError(f"Ошибка в строке {self.current_line + 1}: {str(e)}")

    def parse_array(self, array_str):
        content = array_str[1:-1].strip()
        if not content:
            return []
        
        elements = []
        for item in content.split(','):
            item = item.strip()
            if not item:
                continue
            
            try:
                # Пробуем сначала как целое число, потом как float
                try:
                    elements.append(int(item))
                except ValueError:
                    elements.append(float(item))
            except ValueError:
                raise SyntaxError(f"Некорректное значение '{item}' в массиве")
                
        return elements

    def evaluate_expression(self, expr):
        # Проверяем, является ли это вызовом max
        if expr.startswith('max(') and expr.endswith(')'):
            args_str = expr[4:-1].strip()
            if args_str in self.variables:
                # Если аргумент - это имя переменной
                value = self.variables[args_str]
                if isinstance(value, list):
                    return float(max(value))
            else:
                # Если аргументы переданы напрямую
                try:
                    args = [float(x.strip()) for x in args_str.split(',')]
                    return max(args)
                except ValueError:
                    raise ValueError(f"Некорректные аргументы для функции max: {args_str}")
        
        # Если это не max, обрабатываем как обычное выражение
        for name, value in self.variables.items():
            if isinstance(value, (int, float)):
                expr = re.sub(r'\b' + name + r'\b', str(value), expr)
        
        try:
            safe_dict = {'__builtins__': None}
            return eval(expr, {"__builtins__": None}, safe_dict)
        except Exception as e:
            raise ValueError(f"Ошибка в выражении: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Конвертер конфигурационных файлов')
    parser.add_argument('--input', required=True, help='Входной конфигурационный файл')
    parser.add_argument('--output', help='Выходной TOML файл (по умолчанию: input_config.toml)', default=None)
    args = parser.parse_args()

    config_parser = ConfigParser()
    result = config_parser.parse_file(args.input)
    
    output = {
        "variables": config_parser.variables,
        "expressions": result
    }
    
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(args.input)[0]
        output_file = f"{base_name}_config.toml"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(tomli_w.dumps(output))

if __name__ == '__main__':
    main()
