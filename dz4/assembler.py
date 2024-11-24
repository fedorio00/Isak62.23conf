import re
import yaml
from typing import List, Tuple
from instruction import Instruction, InstructionType, encode_instruction

class Assembler:
    def __init__(self):
        self.instructions = []
        self.labels = {}

    def parse_line(self, line: str) -> Tuple[str, List[str]]:
        """Разбирает строку на команду и операнды."""
        line = line.strip()
        if not line or line.startswith(';'):
            return None, []
        
        # Удаляем комментарии
        line = line.split(';')[0].strip()
        
        # Разбираем метки
        if ':' in line:
            label, rest = line.split(':', 1)
            self.labels[label.strip()] = len(self.instructions)
            line = rest.strip()
            if not line:
                return None, []
        
        # Разбираем команду и операнды
        parts = re.split(r'\s+', line)
        command = parts[0].upper()
        operands = [op.strip() for op in ' '.join(parts[1:]).split(',') if op.strip()]
        
        return command, operands

    def assemble(self, source_path: str, output_path: str, log_path: str) -> None:
        """Собирает программу из исходного файла."""
        with open(source_path, 'r') as f:
            lines = f.readlines()

        log_data = []
        binary_data = bytearray()

        for line_num, line in enumerate(lines, 1):
            command, operands = self.parse_line(line)
            if not command:
                continue

            try:
                if command == 'LOAD':
                    # LOAD addr, const
                    addr = int(operands[0])
                    const = int(operands[1])
                    instr = Instruction(InstructionType.LOAD_CONST, [addr, const])
                
                elif command == 'READ':
                    # READ dest, src, offset
                    dest = int(operands[0])
                    src = int(operands[1])
                    offset = int(operands[2]) if len(operands) > 2 else 0
                    instr = Instruction(InstructionType.READ_MEMORY, [dest, src, offset])
                
                elif command == 'WRITE':
                    # WRITE src, dest
                    src = int(operands[0])
                    dest = int(operands[1])
                    instr = Instruction(InstructionType.WRITE_MEMORY, [src, dest])
                
                elif command == 'BITREV':
                    # BITREV dest, src
                    dest = int(operands[0])
                    src = int(operands[1])
                    instr = Instruction(InstructionType.BITREVERSE, [dest, src])
                
                else:
                    raise ValueError(f"Unknown command: {command}")

                encoded = encode_instruction(instr)
                binary_data.extend(encoded)
                
                # Логируем инструкцию
                log_data.append({
                    'line': line_num,
                    'command': command,
                    'operands': operands,
                    'bytes': [f"0x{b:02X}" for b in encoded]
                })

            except Exception as e:
                raise ValueError(f"Error at line {line_num}: {str(e)}")

        # Записываем бинарный файл
        with open(output_path, 'wb') as f:
            f.write(binary_data)

        # Записываем лог
        with open(log_path, 'w') as f:
            yaml.dump(log_data, f, sort_keys=False)
