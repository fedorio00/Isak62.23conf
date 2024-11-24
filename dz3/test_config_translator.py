import pytest
import os
from config_translator import ConfigParser

def test_comments():
    config = """
    ! Single line comment
    =begin
    Multiline
    comment
    =end
    var x = 1;
    """
    parser = ConfigParser()
    with open('test_config.txt', 'w') as f:
        f.write(config)
    result = parser.parse_file('test_config.txt')
    os.remove('test_config.txt')
    assert 'x' in parser.variables
    assert parser.variables['x'] == 1.0

def test_arrays():
    config = """
    var arr = { 1, 2, 3, 4 };
    """
    parser = ConfigParser()
    with open('test_config.txt', 'w') as f:
        f.write(config)
    result = parser.parse_file('test_config.txt')
    os.remove('test_config.txt')
    assert 'arr' in parser.variables
    assert parser.variables['arr'] == [1.0, 2.0, 3.0, 4.0]

def test_expressions():
    config = """
    var x = 10;
    var y = 20;
    [x + y]
    """
    parser = ConfigParser()
    with open('test_config.txt', 'w') as f:
        f.write(config)
    result = parser.parse_file('test_config.txt')
    os.remove('test_config.txt')
    assert result['expression_result'] == 30.0

def test_max_function():
    config = """
    var arr = { 1, 5, 3 };
    [max(1, 2, 3)]
    """
    parser = ConfigParser()
    with open('test_config.txt', 'w') as f:
        f.write(config)
    result = parser.parse_file('test_config.txt')
    os.remove('test_config.txt')
    assert result['expression_result'] == 3.0

def test_syntax_error():
    config = """
    var x = ;
    """
    parser = ConfigParser()
    with open('test_config.txt', 'w') as f:
        f.write(config)
    with pytest.raises(SyntaxError):
        parser.parse_file('test_config.txt')
    os.remove('test_config.txt')

def test_unclosed_comment():
    config = """
    =begin
    Unclosed comment
    """
    parser = ConfigParser()
    with open('test_config.txt', 'w') as f:
        f.write(config)
    with pytest.raises(SyntaxError):
        parser.parse_file('test_config.txt')
    os.remove('test_config.txt')

def test_constant_expression():
    config = """
    var x = 5;
    .[x + 1]
    """
    parser = ConfigParser()
    with open('test_config.txt', 'w') as f:
        f.write(config)
    result = parser.parse_file('test_config.txt')
    os.remove('test_config.txt')
    assert result['expression_result'] == 6.0
