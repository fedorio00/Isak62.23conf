import unittest
from unittest.mock import patch, mock_open
from git_dependency_graph import DependencyGraphVisualizer, GitCommitNode

class TestDependencyGraphVisualizer(unittest.TestCase):
    def setUp(self):
        self.sample_config = {
            'paths': {
                'visualizer': 'mermaid-cli',
                'repository': './test-repo',
                'output': 'output.md',
                'target_file': 'example.txt'
            }
        }
        with patch('tomli.load', return_value=self.sample_config):
            with patch('builtins.open', mock_open()):
                self.visualizer = DependencyGraphVisualizer('config.toml')

    def test_load_config(self):
        self.assertEqual(self.visualizer.config, self.sample_config)

    def test_get_file_history(self):
        git_output = "abc123|First commit\ndef456|Second commit"
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = git_output
            commits = self.visualizer._get_file_history('example.txt')
            
            self.assertEqual(len(commits), 2)
            self.assertEqual(commits[0].commit_hash, 'abc123')
            self.assertEqual(commits[0].message, 'First commit')
            self.assertEqual(commits[1].commit_hash, 'def456')
            self.assertEqual(commits[1].message, 'Second commit')

    def test_get_commit_parents(self):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "abc123 def456 ghi789\n"
            parents = self.visualizer._get_commit_parents('abc123')
            self.assertEqual(parents, ['def456', 'ghi789'])

    def test_generate_mermaid(self):
        commits = [
            GitCommitNode('abc123', 'First commit'),
            GitCommitNode('def456', 'Second commit')
        ]
        commits[0].parents = ['def456']
        
        mermaid_code = self.visualizer.generate_mermaid(commits)
        expected = (
            "graph TD;\n"
            '    abc123["First commit"]\n'
            '    def456["Second commit"]\n'
            '    abc123 --> def456'
        )
        self.assertEqual(mermaid_code, expected)

    def test_visualize(self):
        with patch.object(self.visualizer, '_get_file_history') as mock_history:
            with patch.object(self.visualizer, '_get_commit_parents') as mock_parents:
                with patch('builtins.open', mock_open()) as mock_file:
                    # Подготовка тестовых данных
                    commit = GitCommitNode('abc123', 'Test commit')
                    mock_history.return_value = [commit]
                    mock_parents.return_value = ['def456']
                    
                    # Вызов тестируемого метода
                    result = self.visualizer.visualize()
                    
                    # Проверка результатов
                    self.assertIn('abc123', result)
                    self.assertIn('Test commit', result)
                    mock_file.assert_called_with('output.md', 'w')

if __name__ == '__main__':
    unittest.main()
