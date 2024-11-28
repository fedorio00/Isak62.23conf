; Тестовая программа для проверки кодирования инструкций
; Каждая команда должна генерировать конкретные байты

; 1. LOAD_CONST (загрузка константы)
; A = 60 (0x7C), B = 301, C = 788
; Ожидаемые байты: 0x7C, 0x4B, 0x50, 0x0C, 0x00, 0x00
LOAD 31, 78

; 2. READ_MEMORY (чтение из памяти)
; A = 39 (0xA7), B = 766, C = 333, D = 13
; Ожидаемые байты: 0xA7, 0xBF, 0x34, 0x45, 0x03, 0x00
READ 766, 33, 3

; 3. WRITE_MEMORY (запись в память)
; A = 53 (0x75), B = 581, C = 179
; Ожидаемые байты: 0x75, 0x91, 0xCC, 0x02, 0x00, 0x00
WRITE 51, 19

; 4. BITREVERSE (битовый реверс)
; A = 28 (0x5C), B = 253, C = 51
; Ожидаемые байты: 0x5C, 0x3F, 0xCC, 0x00, 0x00, 0x00
BITREV 23, 5
