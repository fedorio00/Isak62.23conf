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
                with tarfile.open(self.fs_path, 'w:'):
                    pass
            self.tar = tarfile.open(self.fs_path, 'a:')
        except Exception as e:
            print(f"Ошибка при загрузке файловой системы: {e}")
            raise

    def do_ls(self, args):
        """Реализация команды ls"""
        path = self.current_dir.strip('/').replace('\\', '/')
        members = self.tar.getmembers()
        
        # Если мы в корневом каталоге
        if not path:
            for member in members:
                name_parts = member.name.split('/')
                if len(name_parts) == 1:
                    print(name_parts[0])
        else:
            # Для подкаталогов
            for member in members:
                if member.name.startswith(path + '/'):
                    remaining = member.name[len(path)+1:]
                    if remaining and '/' not in remaining:
                        print(remaining)

    def do_cd(self, args):
        """Реализация команды cd"""
        if not args or args == '/':
            self.current_dir = '/'
            return

        if args.startswith('/'):
            new_path = args
        else:
            new_path = os.path.normpath(os.path.join(self.current_dir, args))
        
        new_path = new_path.replace('\\', '/')
        if self._path_exists(new_path):
            self.current_dir = new_path
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
        # Для учебного эмулятора просто выводим фиктивного пользователя
        print("student    pts/0        2024-03-21 10:00")

    def do_tail(self, args):
        """Показать последние строки файла"""
        if not args:
            print("Использование: tail <имя_файла>")
            return

        try:
            file_path = os.path.normpath(os.path.join(self.current_dir, args)).replace('\\', '/').strip('/')
            
            # Закрываем текущий архив
            self.tar.close()
            
            # Открываем архив в режиме чтения
            with tarfile.open(self.fs_path, 'r:') as tar:
                try:
                    member = tar.getmember(file_path)
                    if not member.isfile():
                        print(f"Ошибка: {args} не является файлом")
                        return
                    
                    f = tar.extractfile(member)
                    if f is None:
                        print(f"Ошибка: невозможно прочитать файл {args}")
                        return
                    
                    try:
                        content = f.read().decode('utf-8')
                        lines = content.splitlines()[-10:]
                        if lines:
                            print('\n'.join(lines))
                    finally:
                        f.close()
                        
                except KeyError:
                    print(f"Ошибка: файл {args} не найден")
                    
        except Exception as e:
            print(f"Ошибка: {e}")
        
        finally:
            # Переоткрываем архив в режиме добавления
            self._load_virtual_fs()

    def do_cp(self, args):
        """Копировать файл или каталог"""
        if not args:
            print("Использование: cp <источник> <назначение>")
            return
            
        try:
            args_list = shlex.split(args)
            if len(args_list) != 2:
                print("Использование: cp <источник> <назначение>")
                return
                
            src, dest = args_list
            src_path = os.path.normpath(os.path.join(self.current_dir, src)).replace('\\', '/').strip('/')
            dest_path = os.path.normpath(os.path.join(self.current_dir, dest)).replace('\\', '/').strip('/')
            
            try:
                src_member = self.tar.getmember(src_path)
                if not src_member.isfile():
                    print(f"Ошибка: {src} не является файлом")
                    return
                
                # Создаем новый архив
                temp_tar_path = self.fs_path + '.temp'
                
                # Закрываем текущий архив перед копированием
                self.tar.close()
                
                with tarfile.open(self.fs_path, 'r:') as src_tar, \
                     tarfile.open(temp_tar_path, 'w:') as new_tar:
                    
                    # Копируем все существующие файлы
                    for member in src_tar.getmembers():
                        if member.name != dest_path:
                            if member.isfile():
                                with src_tar.extractfile(member) as f:
                                    new_tar.addfile(member, f)
                            else:
                                new_tar.addfile(member)
                    
                    # Копируем исходный файл в новое место
                    dest_info = tarfile.TarInfo(dest_path)
                    dest_info.size = src_member.size
                    dest_info.mode = src_member.mode
                    dest_info.type = src_member.type
                    
                    with src_tar.extractfile(src_path) as f:
                        new_tar.addfile(dest_info, f)
                
                # Заменяем старый архив новым
                os.replace(temp_tar_path, self.fs_path)
                print(f"Файл {src} успешно скопирован в {dest}")
                
            except KeyError:
                print(f"Ошибка: файл {src} не найден")
                return
                
        except Exception as e:
            print(f"Ошибка при копировании: {e}")
            if 'temp_tar_path' in locals() and os.path.exists(temp_tar_path):
                os.remove(temp_tar_path)
            
        finally:
            # Переоткрываем архив
            self._load_virtual_fs()

def main():
    config_path = 'config.toml'
    shell = ShellEmulator(config_path)
    shell.cmdloop()
if __name__ == '__main__':
    main()