import yaml
from typing import List, Dict
from instruction import Instruction, InstructionType, decode_instruction, bitreverse

class VirtualMachine:
    def __init__(self, memory_size: int = 4096):
        self.memory = [0] * memory_size
        self.pc = 0  # program counter

    def load_program(self, binary_data: bytes) -> None:
        """Загружает программу в память."""
        self.program = []
        offset = 0
        while offset < len(binary_data):
            instr_bytes = binary_data[offset:offset + 6]
            if len(instr_bytes) < 6:
                break
            self.program.append(decode_instruction(instr_bytes))
            offset += 6
        self.pc = 0

    def execute_instruction(self, instr: Instruction) -> None:
        """Выполняет одну инструкцию."""
        if instr.type == InstructionType.LOAD_CONST:
            addr, const = instr.operands
            self.memory[addr] = const

        elif instr.type == InstructionType.READ_MEMORY:
            dest, src, offset = instr.operands
            addr = self.memory[src] + offset
            self.memory[dest] = self.memory[addr]

        elif instr.type == InstructionType.WRITE_MEMORY:
            src, dest = instr.operands
            self.memory[dest] = self.memory[src]

        elif instr.type == InstructionType.BITREVERSE:
            dest, src = instr.operands
            self.memory[dest] = bitreverse(self.memory[src])

    def run(self) -> None:
        """Выполняет программу."""
        while self.pc < len(self.program):
            self.execute_instruction(self.program[self.pc])
            self.pc += 1

    def dump_memory(self, start: int, end: int, output_path: str) -> None:
        """Сохраняет содержимое памяти в указанном диапазоне."""
        memory_dump = {
            'memory_range': {
                'start': start,
                'end': end
            },
            'values': {i: self.memory[i] for i in range(start, end + 1)}
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(memory_dump, f, sort_keys=False)
