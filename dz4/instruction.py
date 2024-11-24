from dataclasses import dataclass
from enum import Enum, auto

class InstructionType(Enum):
    LOAD_CONST = 60  # Загрузка константы
    READ_MEMORY = 39  # Чтение значения из памяти
    WRITE_MEMORY = 53  # Запись значения в память
    BITREVERSE = 28  # Унарная операция bitreverse()

@dataclass
class Instruction:
    type: InstructionType
    operands: list[int]
    size: int = 6  # все команды имеют размер 6 байт

def bitreverse(value: int) -> int:
    """Выполняет операцию bitreverse над значением."""
    # Предполагаем, что значение 32-битное
    binary = format(value & 0xFFFFFFFF, '032b')
    reversed_binary = binary[::-1]
    return int(reversed_binary, 2)

def encode_instruction(instr: Instruction) -> bytes:
    """Кодирует инструкцию в байты."""
    if instr.type == InstructionType.LOAD_CONST:
        # A(6 бит) | B(12 бит) | C(25 бит)
        result = (instr.type.value & 0x3F) << 42
        result |= (instr.operands[0] & 0xFFF) << 25
        result |= (instr.operands[1] & 0x1FFFFFF)
        return result.to_bytes(6, byteorder='big')
    
    elif instr.type == InstructionType.READ_MEMORY:
        # A(6 бит) | B(12 бит) | C(12 бит) | D(5 бит)
        result = (instr.type.value & 0x3F) << 29
        result |= (instr.operands[0] & 0xFFF) << 17
        result |= (instr.operands[1] & 0xFFF) << 5
        result |= (instr.operands[2] & 0x1F)
        return result.to_bytes(6, byteorder='big')
    
    elif instr.type == InstructionType.WRITE_MEMORY:
        # A(6 бит) | B(12 бит) | C(12 бит)
        result = (instr.type.value & 0x3F) << 24
        result |= (instr.operands[0] & 0xFFF) << 12
        result |= (instr.operands[1] & 0xFFF)
        return result.to_bytes(6, byteorder='big')
    
    elif instr.type == InstructionType.BITREVERSE:
        # A(6 бит) | B(12 бит) | C(12 бит)
        result = (instr.type.value & 0x3F) << 24
        result |= (instr.operands[0] & 0xFFF) << 12
        result |= (instr.operands[1] & 0xFFF)
        return result.to_bytes(6, byteorder='big')
    
    raise ValueError(f"Unknown instruction type: {instr.type}")

def decode_instruction(data: bytes) -> Instruction:
    """Декодирует байты в инструкцию."""
    if len(data) != 6:
        raise ValueError("Invalid instruction length")
    
    value = int.from_bytes(data, byteorder='big')
    
    # Проверяем старшие биты для определения типа инструкции
    if (value >> 42) & 0x3F:  # LOAD_CONST
        instruction_type = InstructionType.LOAD_CONST
        addr = (value >> 25) & 0xFFF
        const = value & 0x1FFFFFF
        return Instruction(instruction_type, [addr, const])
    
    elif (value >> 29) & 0x3F:  # READ_MEMORY
        instruction_type = InstructionType.READ_MEMORY
        addr1 = (value >> 17) & 0xFFF
        addr2 = (value >> 5) & 0xFFF
        offset = value & 0x1F
        return Instruction(instruction_type, [addr1, addr2, offset])
    
    elif (value >> 24) & 0x3F:  # WRITE_MEMORY или BITREVERSE
        instruction_type_value = (value >> 24) & 0x3F
        addr1 = (value >> 12) & 0xFFF
        addr2 = value & 0xFFF
        
        if instruction_type_value == InstructionType.WRITE_MEMORY.value:
            return Instruction(InstructionType.WRITE_MEMORY, [addr1, addr2])
        elif instruction_type_value == InstructionType.BITREVERSE.value:
            return Instruction(InstructionType.BITREVERSE, [addr1, addr2])
    
    raise ValueError(f"Unknown instruction type: {value >> 24 & 0x3F}")
