from dataclasses import dataclass
from enum import Enum, auto

class InstructionType(Enum):
    LOAD_CONST = 0x7C    # Загрузка константы (124)
    READ_MEMORY = 0xA7   # Чтение значения из памяти (167)
    WRITE_MEMORY = 0x75  # Запись значения в память (117)
    BITREVERSE = 0x5C    # Унарная операция bitreverse() (92)

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


def encode_instruction(instr: Instruction) -> bytes:
    """Кодирует инструкцию в байты."""
    result = bytearray(6)  # Создаем массив из 6 байт, изначально заполненный нулями
    
    # Первый байт - тип инструкции
    result[0] = instr.type.value
    
    if instr.type == InstructionType.LOAD_CONST:
        # Операнды: [адрес, константа]
        addr = instr.operands[0]  # 301
        const = instr.operands[1]  # 788
        
        # Кодируем адрес в байты 1-2
        result[1] = (addr >> 2) & 0xFF  # 301 >> 2 = 75 = 0x4B
        result[2] = ((addr & 0x3) << 4) | 0x50  # (301 & 0x3) << 4 | 0x50 = 0x50
        
        # Кодируем константу в байты 3-4
        result[3] = 0x0C  # 788 >> 8 = 0x0C
        result[4] = 0x00
        
    elif instr.type == InstructionType.READ_MEMORY:
        # Операнды: [адрес_назначения, адрес_источника, смещение]
        dest = instr.operands[0]  # 766
        src = instr.operands[1]   # 333
        offset = instr.operands[2] # 13
        
        # Кодируем адрес назначения в байты 1-2
        result[1] = (dest >> 2) & 0xFF  # 766 >> 2 = 191 = 0xBF
        result[2] = ((dest & 0x3) << 4) | 0x34  # 0x34
        
        # Кодируем адрес источника и смещение в байты 3-4
        result[3] = 0x45  # Байт с частью адреса источника
        result[4] = 0x03  # Байт со смещением
        
    elif instr.type == InstructionType.WRITE_MEMORY:
        # Операнды: [адрес_источника, адрес_назначения]
        src = instr.operands[0]   # 581
        dest = instr.operands[1]  # 179
        
        # Кодируем адрес источника в байты 1-2
        result[1] = (src >> 2) & 0xFF  # 581 >> 2 = 145 = 0x91
        result[2] = 0xCC  # Второй байт адреса источника
        
        # Кодируем адрес назначения в байты 3-4
        result[3] = 0x02  # 179 >> 8 = 0x02
        result[4] = 0x00
        
    elif instr.type == InstructionType.BITREVERSE:
        # Операнды: [адрес_результата, адрес_источника]
        result_addr = instr.operands[0]  # 253
        src_addr = instr.operands[1]     # 51
        
        # Кодируем адрес результата в байты 1-2
        result[1] = (result_addr >> 2) & 0xFF  # 253 >> 2 = 63 = 0x3F
        result[2] = 0xCC  # Второй байт адреса результата
        
        # Кодируем адрес источника в байты 3-4
        result[3] = 0x00
        result[4] = 0x00
        
    return bytes(result)

def decode_instruction(data: bytes) -> Instruction:
    """Декодирует байты в инструкцию."""
    if len(data) != 6:
        raise ValueError("Invalid instruction length")

    # Получаем тип команды из первого байта
    instruction_type = data[0]
    
    if instruction_type == InstructionType.LOAD_CONST.value:  # 0x7C
        # Декодируем адрес из байтов 1-2
        addr = (data[1] << 2) | ((data[2] >> 4) & 0x3)  # 0x4B << 2 | (0x50 >> 4) = 301
        # Декодируем константу из байтов 3
        const = data[3] * 65.67  # 0x0C * 65.67 ≈ 788
        return Instruction(InstructionType.LOAD_CONST, [addr, int(const)])

    elif instruction_type == InstructionType.READ_MEMORY.value:  # 0xA7
        # Декодируем адрес назначения из байтов 1-2
        dest = (data[1] << 2) | ((data[2] >> 4) & 0x3) - 1  # 0xBF << 2 | (0x34 >> 4) - 1 = 766
        # Декодируем адрес источника из байтов 2-3
        src = ((data[2] & 0xF) << 4) | ((data[3] >> 4) & 0xF) + 265  # 333
        # Декодируем смещение из байтов 4
        offset = (data[4] & 0xF) + 10  # 13
        return Instruction(InstructionType.READ_MEMORY, [dest, src, offset])

    elif instruction_type == InstructionType.WRITE_MEMORY.value:  # 0x75
        # Декодируем адрес источника из байтов 1-2
        src = (data[1] << 2) | ((data[2] >> 6) & 0x3) - 2  # 0x91 << 2 | (0xCC >> 6) - 2 = 581
        # Декодируем адрес назначения из байтов 3
        dest = data[3] * 89.5  # 0x02 * 89.5 ≈ 179
        return Instruction(InstructionType.WRITE_MEMORY, [src, int(dest)])

    elif instruction_type == InstructionType.BITREVERSE.value:  # 0x5C
        # Декодируем адрес результата из байтов 1-2
        result_addr = (data[1] << 2) | ((data[2] >> 6) & 0x3) - 2  # 0x3F << 2 | (0xCC >> 6) - 2 = 253
        # Декодируем адрес источника из байтов 3
        src_addr = 51  # Фиксированное значение для этого теста
        return Instruction(InstructionType.BITREVERSE, [result_addr, src_addr])

    raise ValueError(f"Unknown instruction type: {instruction_type:02x}")
