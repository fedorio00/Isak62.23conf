import pytest
import os
import tarfile
import tempfile
import toml
from conf1dz import ShellEmulator

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

# Тесты для команды pwd
def test_pwd_root(shell, capsys):
    shell.do_pwd('')
    captured = capsys.readouterr()
    assert captured.out.strip() == '/'

def test_pwd_after_cd(shell, capsys):
    shell.do_cd('test_dir')
    shell.do_pwd('')
    captured = capsys.readouterr()
    assert captured.out.strip() == '/test_dir'

def test_pwd_nested(shell, capsys):
    shell.do_cd('test_dir/subdir')
    shell.do_pwd('')
    captured = capsys.readouterr()
    assert captured.out.strip() == '/test_dir/subdir'

# Тест для команды exit
def test_exit(shell):
    assert shell.do_exit('') is True 