import os
import cmd
import tarfile
import toml
import shlex

class ShellEmulator(cmd.Cmd):
    prompt = '$ '
    
    def __init__(self, config_path):
        super().__init__()
        self.current_dir = '/'
        self.config = self._load_config(config_path)
        self.fs_path = self.config.get('fs_path')
        self._load_virtual_fs()

    def _load_config(self, config_path):
        """Загрузка конфигурации из toml файла"""
        with open(config_path, 'r') as f:
            return toml.load(f)

    def _load_virtual_fs(self):
        """Загрузка виртуальной файловой системы из tar архива"""
        try:
            if not os.path.exists(self.fs_path):
                # Создаем пустой архив, если его нет
                with tarfile.open(self.fs_path, 'w'):
                    pass
            self.tar = tarfile.open(self.fs_path, 'r')
        except Exception as e:
            print(f"Ошибка при загрузке файловой системы: {e}")
            raise

    def do_ls(self, args):
        """Реализация команды ls"""
        path = self.current_dir.replace('\\', '/').strip('/')
        members = self.tar.getmembers()
        
        # Если мы в корневом каталоге
        if not path:
            for member in members:
                if '/' not in member.name:
                    print(member.name)
        else:
            # Для подкаталогов
            for member in members:
                if member.name.startswith(path + '/') and member.name[len(path)+1:].count('/') == 0:
                    print(os.path.basename(member.name))

    def do_cd(self, args):
        """Реализация команды cd"""
        if not args:
            self.current_dir = '/'
            print(self.current_dir)
            return

        new_path = os.path.normpath(os.path.join(self.current_dir, args))
        if self._path_exists(new_path):
            self.current_dir = new_path
            print(self.current_dir)
        else:
            print(f"cd: {args}: Нет такого каталога")

    def do_exit(self, args):
        """Выход из эмулятора"""
        return True

    def _path_exists(self, path):
        """Проверка существования пути в виртуальной ФС"""
        if path == '/':
            return True
        
        members = self.tar.getmembers()
        stripped_path = path.replace('\\', '/').strip('/')
        
        # Проверяем существование каталога
        exists = any(
            m.name == stripped_path or  # Точное совпадение
            stripped_path == os.path.dirname(m.name) or  # Путь является родительским каталогом
            m.name.startswith(stripped_path + '/')  # Путь является префиксом
            for m in members
        )
        
        return exists

    def do_who(self, args):
        """Показать пользователей, вошедших в систему"""
        users = os.popen('who').read()
        print(users)

    def do_tail(self, args):
        """Показать последние строки файла"""
        if not args:
            print("Использование: tail <имя_файла>")
            return
        try:
            with open(args, 'r') as f:
                lines = f.readlines()[-10:]  # Получаем последние 10 строк
                print(''.join(lines))
        except FileNotFoundError:
            print(f"Ошибка: файл {args} не найден.")
        except Exception as e:
            print(f"Ошибка: {e}")

    def do_cp(self, args):
        """Копировать файл или каталог"""
        if not args:
            print("Использование: cp <источник> <назначение>")
            return
        src, dest = args.split()
        try:
            os.system(f'cp {src} {dest}')
            print(f"Копирование {src} в {dest} завершено.")
        except Exception as e:
            print(f"Ошибка: {e}")

def main():
    config_path = 'config.toml'
    shell = ShellEmulator(config_path)
    shell.cmdloop()
if __name__ == '__main__':
    main()