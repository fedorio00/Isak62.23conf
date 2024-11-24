import subprocess
import tomli
from typing import List, Dict, Set
import os

class GitCommitNode:
    def __init__(self, commit_hash: str, message: str):
        self.commit_hash = commit_hash
        self.message = message
        self.parents: List[str] = []

class DependencyGraphVisualizer:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: str) -> dict:
        """Загрузка конфигурации из TOML файла."""
        with open(config_path, 'rb') as f:
            return tomli.load(f)

    def _get_file_history(self, file_path: str) -> List[GitCommitNode]:
        """Получение истории коммитов для конкретного файла."""
        cmd = ['git', 'log', '--follow', '--format=%H|%s', '--', file_path]
        result = subprocess.run(cmd, 
                              cwd=self.config['paths']['repository'],
                              capture_output=True, 
                              text=True)
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                commit_hash, message = line.split('|', 1)
                node = GitCommitNode(commit_hash, message)
                commits.append(node)
        return commits

    def _get_commit_parents(self, commit_hash: str) -> List[str]:
        """Получение родительских коммитов для заданного коммита."""
        cmd = ['git', 'rev-list', '--parents', '-n', '1', commit_hash]
        result = subprocess.run(cmd, 
                              cwd=self.config['paths']['repository'],
                              capture_output=True, 
                              text=True)
        
        # Первый хэш - текущий коммит, остальные - родители
        hashes = result.stdout.strip().split()
        return hashes[1:] if len(hashes) > 1 else []

    def generate_mermaid(self, commits: List[GitCommitNode]) -> str:
        """Генерация Mermaid-представления графа."""
        mermaid_code = ["graph TD;"]
        
        # Добавляем узлы
        for commit in commits:
            # Экранируем специальные символы в сообщении
            safe_message = commit.message.replace('"', '\\"')
            # Используем короткий хэш для лучшей читаемости
            short_hash = commit.commit_hash[:7]
            mermaid_code.append(f'    {short_hash}["{safe_message}"]')
        
        # Добавляем связи с родителями
        for commit in commits:
            for parent in commit.parents:
                # Используем короткие хэши для связей
                short_hash = commit.commit_hash[:7]
                short_parent = parent[:7]
                mermaid_code.append(f'    {short_hash} --> {short_parent}')
        
        return '\n'.join(mermaid_code)

    def visualize(self) -> str:
        """Основной метод для создания визуализации графа зависимостей."""
        target_file = self.config['paths']['target_file']
        commits = self._get_file_history(target_file)
        
        # Получаем родителей для каждого коммита
        for commit in commits:
            commit.parents = self._get_commit_parents(commit.commit_hash)
        
        # Генерируем Mermaid-код
        mermaid_code = self.generate_mermaid(commits)
        
        # Записываем результат в файл
        output_path = self.config['paths']['output']
        with open(output_path, 'w') as f:
            f.write('```mermaid\n')
            f.write(mermaid_code)
            f.write('\n```\n')
        
        return mermaid_code

def main():
    visualizer = DependencyGraphVisualizer('config.toml')
    mermaid_code = visualizer.visualize()
    print(mermaid_code)

if __name__ == '__main__':
    main()
