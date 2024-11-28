from dataclasses import dataclass
from enum import Enum, auto

class InstructionType(Enum):
    LOAD_CONST = 0x3C    # биты 0-5: 111100
    READ_MEMORY = 0x27   # биты 0-5: 100111
    WRITE_MEMORY = 0x35  # биты 0-5: 110101
    BITREVERSE = 0x1C    # биты 0-5: 011100

@dataclass
class Instruction:
    type: InstructionType
    operands: list[int]
    size: int = 6  # все команды имеют размер 6 байт

def bitreverse(value: int) -> int:
    """Выполняет операцию bitreverse над 32-битным значением."""
    # Убеждаемся, что значение — строго 32-битное
    value &= 0xFFFFFFFF  # Обрезаем до 32 бит
    binary = f"{value:032b}"  # Преобразуем в строку двоичного числа длиной 32 бита
    reversed_binary = binary[::-1]  # Разворачиваем строку
    return int(reversed_binary, 2)  # Возвращаем число, преобразованное обратно в int


def encode_instruction(instruction: Instruction) -> bytes:
    """Кодирует инструкцию в последовательность байтов."""
    data = bytearray(6)  # 6 байт = 48 бит

    # Тип команды всегда в битах 0-5 первого байта
    data[0] = instruction.type.value  # Записываем полный код команды

    if instruction.type == InstructionType.LOAD_CONST:
        # B (биты 6-17): 12 бит
        b_value = instruction.operands[0] & 0xFFF  # 12 бит
        data[0] |= (b_value & 0x3) << 6  # 2 младших бита в первый байт
        data[1] = (b_value >> 2) & 0xFF  # следующие 8 бит во второй байт
        data[2] = (b_value >> 10) & 0x3  # 2 старших бита в третий байт
        
        # C (биты 18-42): 25 бит
        c_value = instruction.operands[1] & 0x1FFFFFF  # 25 бит
        data[2] |= (c_value & 0x3F) << 2  # 6 бит в третий байт
        data[3] = (c_value >> 6) & 0xFF   # 8 бит в четвертый байт
        data[4] = (c_value >> 14) & 0xFF  # 8 бит в пятый байт
        data[5] = (c_value >> 22) & 0x7   # 3 бита в шестой байт

    elif instruction.type == InstructionType.READ_MEMORY:
        # B (биты 6-17): 12 бит
        b_value = instruction.operands[0] & 0xFFF
        data[0] |= (b_value & 0x3) << 6
        data[1] = (b_value >> 2) & 0xFF
        data[2] = (b_value >> 10) & 0x3

        # C (биты 18-29): 12 бит
        c_value = instruction.operands[1] & 0xFFF
        data[2] |= (c_value & 0x3F) << 2
        data[3] = (c_value >> 6) & 0x3F

        # D (биты 30-34): 5 бит
        d_value = instruction.operands[2] & 0x1F
        data[3] |= (d_value & 0x3) << 6
        data[4] = (d_value >> 2) & 0x7

    elif instruction.type == InstructionType.WRITE_MEMORY:
        # B (биты 6-17): 12 бит
        b_value = instruction.operands[0] & 0xFFF
        data[0] |= (b_value & 0x3) << 6
        data[1] = (b_value >> 2) & 0xFF
        data[2] = (b_value >> 10) & 0x3

        # C (биты 18-29): 12 бит
        c_value = instruction.operands[1] & 0xFFF
        data[2] |= (c_value & 0x3F) << 2
        data[3] = (c_value >> 6) & 0x3F

    elif instruction.type == InstructionType.BITREVERSE:
        # B (биты 6-17): 12 бит
        b_value = instruction.operands[0] & 0xFFF
        data[0] |= (b_value & 0x3) << 6
        data[1] = (b_value >> 2) & 0xFF
        data[2] = (b_value >> 10) & 0x3
        # C (биты 18-29): 12 бит
        c_value = instruction.operands[1] & 0xFFF
        data[2] |= (c_value & 0x3F) << 2
        data[3] = (c_value >> 6) & 0x3F
    return bytes(data)

def decode_instruction(data: bytes) -> Instruction:
    """Декодирует последовательность байтов в инструкцию."""
    if len(data) != 6:
        raise ValueError("Invalid instruction length")

    # Получаем тип команды из первого байта
    instruction_type = data[0] & 0x3F  # Маскируем биты 6-7
    
    # Для всех команд B находится в битах 6-17
    b_value = ((data[0] >> 6) & 0x3) | (data[1] << 2) | ((data[2] & 0x3) << 10)

    if instruction_type == InstructionType.LOAD_CONST.value:
        # C (биты 18-42): 25 бит
        c_value = ((data[2] >> 2) & 0x3F) | (data[3] << 6) | (data[4] << 14) | ((data[5] & 0x7) << 22)
        return Instruction(InstructionType.LOAD_CONST, [b_value, c_value])

    elif instruction_type == InstructionType.READ_MEMORY.value:
        # C (биты 18-29): 12 бит
        c_value = ((data[2] >> 2) & 0x3F) | ((data[3] & 0x3F) << 6)
        # D (биты 30-34): 5 бит
        d_value = ((data[3] >> 6) & 0x3) | ((data[4] & 0x7) << 2)
        return Instruction(InstructionType.READ_MEMORY, [b_value, c_value, d_value])

    elif instruction_type == InstructionType.WRITE_MEMORY.value:
        # C (биты 18-29): 12 бит
        c_value = ((data[2] >> 2) & 0x3F) | ((data[3] & 0x3F) << 6)
        return Instruction(InstructionType.WRITE_MEMORY, [b_value, c_value])

    elif instruction_type == InstructionType.BITREVERSE.value:
        # C (биты 18-29): 12 бит
        c_value = ((data[2] >> 2) & 0x3F) | ((data[3] & 0x3F) << 6)
        return Instruction(InstructionType.BITREVERSE, [b_value, c_value])

    raise ValueError(f"Unknown instruction type: {instruction_type:02x}")
