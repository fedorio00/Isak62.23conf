import subprocess
import os
from typing import List, Dict, Optional

def parse_toml(config_path: str) -> dict:
    """Простой парсер для TOML файла с конфигурацией."""
    if not os.path.exists(config_path):
        return {
            "paths": {
                "repository": ".",
                "target_file": "example.txt",
                "output": "dependency_graph.md",
                "visualizer": "mermaid-cli"
            }
        }
    
    config = {"paths": {}}
    current_section = None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                if current_section not in config:
                    config[current_section] = {}
            elif '=' in line and current_section:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                config[current_section][key] = value
                
    return config

def get_file_history(repo_path: str, file_path: str) -> List[Dict[str, str]]:
    """Получает историю коммитов для файла."""
    cmd = ['git', 'log', '--follow', '--format=%H|%s', '--', file_path]
    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, encoding='utf-8')
    
    commits = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        commit_hash, message = line.split('|', 1)
        commits.append({
            'hash': commit_hash,
            'message': message,
            'parents': []
        })
    return commits

def get_commit_parents(repo_path: str, commit_hash: str) -> List[str]:
    """Получает список хешей родительских коммитов."""
    cmd = ['git', 'rev-list', '--parents', '-n', '1', commit_hash]
    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, encoding='utf-8')
    
    # Первый хеш - текущий коммит, остальные - родители
    hashes = result.stdout.strip().split()
    return hashes[1:] if len(hashes) > 1 else []

def generate_mermaid(commits: List[Dict[str, str]]) -> str:
    """Генерирует Mermaid-диаграмму."""
    mermaid_lines = ['graph TD;']
    
    # Добавляем узлы
    for commit in commits:
        short_hash = commit['hash'][:7]
        # Экранируем кавычки в сообщении
        safe_message = commit['message'].replace('"', '\\"')
        mermaid_lines.append(f'    {short_hash}["{safe_message}"]')
    
    # Добавляем связи
    for commit in commits:
        short_hash = commit['hash'][:7]
        for parent in commit['parents']:
            short_parent = parent[:7]
            mermaid_lines.append(f'    {short_hash} --> {short_parent}')
    
    return '\n'.join(mermaid_lines)

def create_dependency_graph(config_file: str = 'config.toml') -> str:
    """Создает граф зависимостей для файла."""
    # Загружаем конфигурацию
    config = parse_toml(config_file)
    repo_path = config['paths']['repository']
    target_file = config['paths']['target_file']
    output_file = config['paths']['output']
    
    # Получаем историю коммитов
    commits = get_file_history(repo_path, target_file)
    
    # Получаем родительские коммиты для каждого коммита
    for commit in commits:
        commit['parents'] = get_commit_parents(repo_path, commit['hash'])
    
    # Генерируем Mermaid-диаграмму
    mermaid_code = generate_mermaid(commits)
    
    # Сохраняем результат
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('```mermaid\n')
        f.write(mermaid_code)
        f.write('\n```\n')
    
    return mermaid_code

if __name__ == '__main__':
    create_dependency_graph()
