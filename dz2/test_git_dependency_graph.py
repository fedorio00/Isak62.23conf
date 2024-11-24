import pytest
from unittest.mock import patch, mock_open
from git_dependency_graph import DependencyGraphVisualizer, GitCommitNode

@pytest.fixture
def sample_config():
    return {
        'paths': {
            'visualizer': 'mermaid-cli',
            'repository': './test-repo',
            'output': 'output.md',
            'target_file': 'example.txt'
        }
    }

@pytest.fixture
def visualizer(sample_config):
    with patch('tomli.load', return_value=sample_config):
        with patch('builtins.open', mock_open()):
            return DependencyGraphVisualizer('config.toml')

def test_load_config(visualizer, sample_config):
    assert visualizer.config == sample_config

def test_get_file_history(visualizer):
    git_output = "abc123|First commit\ndef456|Second commit"
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = git_output
        commits = visualizer._get_file_history('example.txt')
        
        assert len(commits) == 2
        assert commits[0].commit_hash == 'abc123'
        assert commits[0].message == 'First commit'
        assert commits[1].commit_hash == 'def456'
        assert commits[1].message == 'Second commit'

def test_get_commit_parents(visualizer):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = "abc123 def456 ghi789\n"
        parents = visualizer._get_commit_parents('abc123')
        assert parents == ['def456', 'ghi789']

def test_generate_mermaid(visualizer):
    commits = [
        GitCommitNode('abc123', 'First commit'),
        GitCommitNode('def456', 'Second commit')
    ]
    commits[0].parents = ['def456']
    
    mermaid_code = visualizer.generate_mermaid(commits)
    expected = (
        "graph TD;\n"
        '    abc123["First commit"]\n'
        '    def456["Second commit"]\n'
        '    abc123 --> def456'
    )
    assert mermaid_code == expected

def test_visualize(visualizer):
    with patch.object(visualizer, '_get_file_history') as mock_history:
        with patch.object(visualizer, '_get_commit_parents') as mock_parents:
            with patch('builtins.open', mock_open()) as mock_file:
                # Подготовка тестовых данных
                commit = GitCommitNode('abc123', 'Test commit')
                mock_history.return_value = [commit]
                mock_parents.return_value = ['def456']
                
                # Вызов тестируемого метода
                result = visualizer.visualize()
                
                # Проверка результатов
                assert 'abc123' in result
                assert 'Test commit' in result
                mock_file.assert_called_with('output.md', 'w')
