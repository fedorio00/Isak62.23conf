import os
import cmd
import tarfile
import toml
import shlex
import tkinter as tk
from tkinter import scrolledtext

class ShellEmulator(cmd.Cmd):
    
    def __init__(self, config_path, output_widget):
        super().__init__()
        self.current_dir = '/'
        self.config = self._load_config(config_path)
        self.fs_path = self.config.get('fs_path')
        self._load_virtual_fs()
        self.output_widget = output_widget
        

    def _load_config(self, config_path):
        with open(config_path, 'r') as f:
            return toml.load(f)

    def _load_virtual_fs(self):
        try:
            if not os.path.exists(self.fs_path):
                with tarfile.open(self.fs_path, 'w:'):
                    pass
            self.tar = tarfile.open(self.fs_path, 'a:')
        except Exception as e:
            self.output_widget.insert(tk.END, f"Ошибка при загрузке файловой системы: {e}\n")
            raise

    def do_ls(self, args):
        self.output_widget.insert(tk.END, "\n")
        path = self.current_dir.strip('/').replace('\\', '/')
        members = self.tar.getmembers()
        output = []

        if not path:
            for member in members:
                name_parts = member.name.split('/')
                if len(name_parts) == 1:
                    output.append(name_parts[0])
        else:
            for member in members:
                if member.name.startswith(path + '/'):
                    remaining = member.name[len(path)+1:]
                    if remaining and '/' not in remaining:
                        output.append(remaining)

        self.output_widget.insert(tk.END, '\n'.join(output))

    def do_cd(self, args):
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
            self.output_widget.insert(tk.END, f"\ncd: {args}: Нет такого каталога\n")

    def do_exit(self, args):
        self.output_widget.quit()  
        self.output_widget.master.destroy()  

    def _path_exists(self, path):
        if path == '/':
            return True
        
        members = self.tar.getmembers()
        stripped_path = path.replace('\\', '/').strip('/')
        
        exists = any(
            m.name == stripped_path or
            stripped_path == os.path.dirname(m.name) or
            m.name.startswith(stripped_path + '/')
            for m in members
        )
        
        return exists

    def do_who(self, args):
        self.output_widget.insert(tk.END, "\n")
        self.output_widget.insert(tk.END, "student    pts/0        2024-03-21 10:00\n")
    
    def do_tail(self, args):
        self.output_widget.insert(tk.END, "\n")
        if not args:
            self.output_widget.insert(tk.END, "Использование: tail <имя_файла>\n")
            return

        try:
            file_path = os.path.normpath(os.path.join(self.current_dir, args)).replace('\\', '/').strip('/')
            self.tar.close()
            with tarfile.open(self.fs_path, 'r:') as tar:
                try:
                    member = tar.getmember(file_path)
                    if not member.isfile():
                        self.output_widget.insert(tk.END, f"Ошибка: {args} не является файлом\n")
                        return
                    
                    f = tar.extractfile(member)
                    if f is None:
                        self.output_widget.insert(tk.END, f"Ошибка: невозможно прочитать файл {args}\n")
                        return
                    
                    content = f.read().decode('utf-8')
                    lines = content.splitlines()[-10:]
                    if lines:
                        self.output_widget.insert(tk.END, '\n'.join(lines) + '\n')
                except KeyError:
                    self.output_widget.insert(tk.END, f"Ошибка: файл {args} не найден\n")
                    
        except Exception as e:
            self.output_widget.insert(tk.END, f"Ошибка: {e}\n")
        
        finally:
            self._load_virtual_fs()
    
    def do_cp(self, args):
        self.output_widget.insert(tk.END, "\n")
        if not args:
            self.output_widget.insert(tk.END, "Использование: cp <источник> <назначение>\n")
            return
            
        try:
            args_list = shlex.split(args)
            if len(args_list) != 2:
                self.output_widget.insert(tk.END, "Использование: cp <источник> <назначение>\n")
                return
                
            src, dest = args_list
            src_path = os.path.normpath(os.path.join(self.current_dir, src)).replace('\\', '/').strip('/')
            dest_path = os.path.normpath(os.path.join(self.current_dir, dest)).replace('\\', '/').strip('/')
            
            try:
                src_member = self.tar.getmember(src_path)
                if not src_member.isfile():
                    self.output_widget.insert(tk.END, f"Ошибка: {src} не является файлом\n")
                    return
                
                temp_tar_path = self.fs_path + '.temp'
                self.tar.close()
                
                with tarfile.open(self.fs_path, 'r:') as src_tar, \
                     tarfile.open(temp_tar_path, 'w:') as new_tar:
                    
                    for member in src_tar.getmembers():
                        if member.name != dest_path:
                            if member.isfile():
                                with src_tar.extractfile(member) as f:
                                    new_tar.addfile(member, f)
                            else:
                                new_tar.addfile(member)
                    
                    dest_info = tarfile.TarInfo(dest_path)
                    dest_info.size = src_member.size
                    dest_info.mode = src_member.mode
                    dest_info.type = src_member.type
                    
                    with src_tar.extractfile(src_path) as f:
                        new_tar.addfile(dest_info, f)
                
                os.replace(temp_tar_path, self.fs_path)
                self.output_widget.insert(tk.END, f"Файл {src} успешно скопирован в {dest}\n")
                
            except KeyError:
                self.output_widget.insert(tk.END, f"Ошибка: файл {src} не найден\n")
                return
                
        except Exception as e:
            self.output_widget.insert(tk.END, f"Ошибка при копировании: {e}\n")
            if 'temp_tar_path' in locals() and os.path.exists(temp_tar_path):
                os.remove(temp_tar_path)
            
        finally:
            self._load_virtual_fs()

    def cmdloop(self):
        while True:
            command = input(self.prompt)
            if self.onecmd(command):
                break

def run_shell():
    root = tk.Tk()
    root.title("Shell Emulator")

    output_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg='black', fg='white', insertbackground='white')
    output_widget.pack(expand=True, fill='both')

    config_path = 'config.toml'
    shell = ShellEmulator(config_path, output_widget)

    def on_enter(event):
        command = output_widget.get("end-2c linestart", "end-1c")
        shell.onecmd(command)
        output_widget.see(tk.END)

    output_widget.bind('<Return>', on_enter)
    root.mainloop()

if __name__ == '__main__':
    run_shell()