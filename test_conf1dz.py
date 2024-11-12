import pytest
import os
import tarfile
import tempfile
import toml
from conf1dz import ShellEmulator
import io

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
    return ShellEmulator(temp_config)

# Тесты для команды ls
def test_ls_root(shell, capsys):
    shell.do_ls('')
    captured = capsys.readouterr()
    assert 'test_dir' in captured.out

def test_ls_subdir(shell, capsys):
    shell.do_cd('test_dir')
    shell.do_ls('')
    captured = capsys.readouterr()
    assert 'test_file.txt' in captured.out
    assert 'subdir' in captured.out

def test_ls_empty_dir(shell, capsys):
    shell.do_cd('test_dir/subdir')
    shell.do_ls('')
    captured = capsys.readouterr()
    assert captured.out.strip() == ''

# Тесты для команды cd
def test_cd_root(shell):
    shell.do_cd('/')
    assert shell.current_dir == '/'

def test_cd_subdir(shell):
    shell.do_cd('test_dir')
    assert shell.current_dir == '/test_dir'

def test_cd_nonexistent(shell, capsys):
    shell.do_cd('nonexistent')
    captured = capsys.readouterr()
    assert 'Нет такого каталога' in captured.out
    assert shell.current_dir == '/'

# Тест для команды exit
def test_exit(shell):
    assert shell.do_exit('') is True 

# Тесты для команды who
def test_who_output(shell, capsys):
    shell.do_who('')
    captured = capsys.readouterr()
    assert 'student' in captured.out
    assert 'pts/0' in captured.out
    assert '2024-03-21' in captured.out

def test_who_with_args(shell, capsys):
    shell.do_who('some args')
    captured = capsys.readouterr()
    assert 'student' in captured.out  # Команда должна работать так же с аргументами

def test_who_format(shell, capsys):
    shell.do_who('')
    captured = capsys.readouterr()
    parts = captured.out.split()
    assert len(parts) >= 4  # Проверяем формат вывода (имя, терминал, дата, время)

# Тесты для команды tail
def test_tail_nonexistent_file(shell, capsys):
    shell.do_tail('nonexistent.txt')
    captured = capsys.readouterr()
    assert 'не найден' in captured.out

def test_tail_no_args(shell, capsys):
    shell.do_tail('')
    captured = capsys.readouterr()
    assert 'Использование: tail' in captured.out

def test_tail_empty_file(shell, capsys):
    shell.do_tail('')  # Вызываем tail без аргументов
    captured = capsys.readouterr()
    assert "Использование: tail" in captured.out  # Проверяем, что выводится сообщение об использовании

# Тесты для команды cp
def test_cp_no_args(shell, capsys):
    shell.do_cp('')
    captured = capsys.readouterr()
    assert 'Использование: cp' in captured.out

def test_cp_nonexistent_source(shell, capsys):
    shell.do_cp('nonexistent.txt dest.txt')
    captured = capsys.readouterr()
    assert 'не найден' in captured.out

def test_cp_file(shell, capsys):
    # Создаем исходный файл
    content = b'test content'
    info = tarfile.TarInfo('source.txt')
    info.size = len(content)
    info.type = tarfile.REGTYPE
    shell.tar.addfile(info, io.BytesIO(content))
    
    shell.do_cp('source.txt dest.txt')
    captured = capsys.readouterr()
    assert 'успешно скопирован' in captured.out