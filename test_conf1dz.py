import pytest
import os
import tarfile
import tempfile
import toml
from conf1dz import ShellEmulator
import io
import tkinter as tk

@pytest.fixture
def temp_fs():
    # Создаем временный tar-архив для тестов
    with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tmp_fs:
        with tarfile.open(tmp_fs.name, 'w') as tar:
            # Создаем тестовую структуру директорий
            info = tarfile.TarInfo('test_dir')
            info.type = tarfile.DIRTYPE
            tar.addfile(info)
            
            info = tarfile.TarInfo('test_dir/test_file.txt')
            info.type = tarfile.REGTYPE
            tar.addfile(info)
            
            info = tarfile.TarInfo('test_dir/subdir')
            info.type = tarfile.DIRTYPE
            tar.addfile(info)
    
    return tmp_fs.name

@pytest.fixture
def temp_config(temp_fs):
    # Создаем временный конфиг
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as tmp_config:
        config = {'fs_path': temp_fs}
        toml.dump(config, tmp_config)
    
    return tmp_config.name

@pytest.fixture
def shell(temp_config):
    # Создаем графический интерфейс для тестов
    root = tk.Tk()
    output_widget = tk.scrolledtext.ScrolledText(root)
    output_widget.pack()
    shell = ShellEmulator(temp_config, output_widget)
    return shell, output_widget

# Тесты для команды ls
def test_ls_root(shell):
    shell[0].do_ls('')
    output = shell[1].get("1.0", tk.END)
    assert 'test_dir' in output

def test_ls_subdir(shell):
    shell[0].do_cd('test_dir')
    shell[0].do_ls('')
    output = shell[1].get("1.0", tk.END)
    assert 'test_file.txt' in output
    assert 'subdir' in output

def test_ls_empty_dir(shell):
    shell[0].do_cd('test_dir/subdir')
    shell[0].do_ls('')
    output = shell[1].get("1.0", tk.END)
    assert output.strip() == ''

# Тесты для команды cd
def test_cd_root(shell):
    shell[0].do_cd('/')
    assert shell[0].current_dir == '/'

def test_cd_subdir(shell):
    shell[0].do_cd('test_dir')
    assert shell[0].current_dir == '/test_dir'

def test_cd_nonexistent(shell):
    shell[0].do_cd('nonexistent')
    output = shell[1].get("1.0", tk.END)
    assert 'Нет такого каталога' in output
    assert shell[0].current_dir == '/'

# Тест для команды exit
def test_exit(shell):
    shell[0].do_exit('')
    assert shell[1].winfo_exists() == 0  # Проверяем, что окно закрыто

# Тесты для команды who
def test_who_output(shell):
    shell[0].do_who('')
    output = shell[1].get("1.0", tk.END)
    assert 'student' in output
    assert 'pts/0' in output
    assert '2024-03-21' in output

def test_who_with_args(shell):
    shell[0].do_who('some args')
    output = shell[1].get("1.0", tk.END)
    assert 'student' in output  # Команда должна работать так же с аргументами

def test_who_format(shell):
    shell[0].do_who('')
    output = shell[1].get("1.0", tk.END)
    parts = output.split()
    assert len(parts) >= 4  # Проверяем формат вывода (имя, терминал, дата, время)

# Тесты для команды tail
def test_tail_nonexistent_file(shell):
    shell[0].do_tail('nonexistent.txt')
    output = shell[1].get("1.0", tk.END)
    assert 'не найден' in output

def test_tail_no_args(shell):
    shell[0].do_tail('')
    output = shell[1].get("1.0", tk.END)
    assert 'Использование: tail' in output

def test_tail_empty_file(shell):
    shell[0].do_tail('')  # Вызываем tail без аргументов
    output = shell[1].get("1.0", tk.END)
    assert "Использование: tail" in output  # Проверяем, что выводится сообщение об использовании

# Тесты для команды cp
def test_cp_no_args(shell):
    shell[0].do_cp('')
    output = shell[1].get("1.0", tk.END)
    assert 'Использование: cp' in output

def test_cp_nonexistent_source(shell):
    shell[0].do_cp('nonexistent.txt dest.txt')
    output = shell[1].get("1.0", tk.END)
    assert 'не найден' in output

def test_cp_file(shell):
    # Создаем исходный файл
    content = b'test content'
    info = tarfile.TarInfo('source.txt')
    info.size = len(content)
    info.type = tarfile.REGTYPE
    shell[0].tar.addfile(info, io.BytesIO(content))
    shell[0].do_cp('source.txt dest.txt')
    output = shell[1].get("1.0", tk.END)
    assert 'успешно скопирован' in output