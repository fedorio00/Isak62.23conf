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
        path = self.current_dir
        members = self.tar.getmembers()
        for member in members:
            if os.path.dirname(member.name) == path.strip('/'):
                print(os.path.basename(member.name))

    def do_cd(self, args):
        """Реализация команды cd"""
        if not args:
            self.current_dir = '/'
            return

        new_path = os.path.normpath(os.path.join(self.current_dir, args))
        if self._path_exists(new_path):
            self.current_dir = new_path
        else:
            print(f"cd: {args}: Нет такого каталога")

    def do_pwd(self, args):
        """Реализация команды pwd"""
        print(self.current_dir)

    def do_exit(self, args):
        """Выход из эмулятора"""
        return True

    def _path_exists(self, path):
        """Проверка существования пути в виртуальной ФС"""
        if path == '/':
            return True
        members = self.tar.getmembers()
        return any(member.name.startswith(path.strip('/')) for member in members)

def main():
    config_path = 'config.toml'
    shell = ShellEmulator(config_path)
    shell.cmdloop()

if __name__ == '__main__':
    main()