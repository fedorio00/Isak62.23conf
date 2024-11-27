import pytest
from unittest.mock import patch, mock_open
from git_graph import (
    parse_toml,
    get_file_history,
    get_commit_parents,
    generate_mermaid,
    create_dependency_graph
)

@pytest.fixture
def sample_config():
    return {
        'paths': {
            'repository': '.',  
            'target_file': 'example.txt',
            'output': 'output.md',
            'visualizer': 'mermaid-cli'
        }
    }

def test_parse_toml():
    config_data = '''[paths]
repository = "."
target_file = "example.txt"
output = "output.md"
visualizer = "mermaid-cli"'''
    with patch('builtins.open', mock_open(read_data=config_data)):
        with patch('os.path.exists', return_value=True):
            config = parse_toml('config.toml')
            assert config['paths']['repository'] == '.'
            assert config['paths']['target_file'] == 'example.txt'
            assert config['paths']['output'] == 'output.md'
            assert config['paths']['visualizer'] == 'mermaid-cli'

def test_get_file_history():
    git_output = "abc123|First commit\ndef456|Second commit"
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = git_output
        commits = get_file_history('.', 'example.txt')
        
        assert len(commits) == 2
        assert commits[0]['hash'] == 'abc123'
        assert commits[0]['message'] == 'First commit'
        assert commits[1]['hash'] == 'def456'
        assert commits[1]['message'] == 'Second commit'

def test_get_commit_parents():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = "abc123 def456 ghi789\n"
        parents = get_commit_parents('.', 'abc123')
        assert parents == ['def456', 'ghi789']

def test_generate_mermaid():
    commits = [
        {'hash': 'abc123', 'message': 'First commit', 'parents': ['def456']},
        {'hash': 'def456', 'message': 'Second commit', 'parents': []}
    ]
    
    mermaid_code = generate_mermaid(commits)
    expected = (
        'graph TD;\n'
        '    abc123["First commit"]\n'
        '    def456["Second commit"]\n'
        '    abc123 --> def456'
    )
    assert mermaid_code == expected

def test_create_dependency_graph(sample_config):
    with patch('git_graph.parse_toml', return_value=sample_config):
        with patch('git_graph.get_file_history') as mock_history:
            mock_history.return_value = [
                {'hash': 'abc123', 'message': 'First commit', 'parents': []}
            ]
            with patch('builtins.open', mock_open()):
                mermaid_code = create_dependency_graph()
                assert 'abc123["First commit"]' in mermaid_code
