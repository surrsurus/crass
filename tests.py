import crass
import pytest

# Test the function inputs
def test_cli_arguments():

  # Too many/few arguments
  with pytest.raises(TypeError):
    crass.cli(['0', '1'], ['2', '3'])
    crass.cli()

  # Check to see if argument is a list
  with pytest.raises(TypeError):
    crass.cli("string")
    crass.cli(1)
    crass.cli(True)

  # Check list length
  with pytest.raises(IndexError):
    crass.cli([])
    crass.cli(['0'])
    crass.cli(['0', '1'])
    crass.cli(['0', '1', '2'])
    crass.cli(['0', '1', '2', '3', '4'])

  # Correct list length
  crass.cli(['0', '1', '2', '3'])


# Make sure src and build aren't nested
def test_cli_nested_check():
  # Improper arrangements
  with pytest.raises(OSError):
    crass.cli(['crass.py', './tests/dir_test_one/src', './tests/dir_test_one/crassfile.crass', './tests/dir_test_one/src/build'])
    crass.cli(['crass.py', './tests/dir_test_two/build/src', './tests/dir_test_two/crassfile.crass', './tests/dir_test_two/build'])
  
  # Correct arrangement
  assert crass.cli(['crass.py', './tests/dir_test_three/src', './tests/dir_test_three/crassfile.crass', './tests/dir_test_three/build']) == None

def test_crass_syntax():
  with pytest.raises(SyntaxError):
    crass.buildAST('./tests/ast_tests/crass_test_one.crass')
    crass.buildAST('./tests/ast_tests/crass_test_two.crass')

  # Test a proper crassfile
  crass.buildAST('./tests/ast_tests/crass_test_three.crass')
  assert crass.AST['id']['id'] == 'id success'
  assert crass.AST['class']['class'] == 'class success'
  assert crass.AST['id']['really_long_id'] == 'really long id with a long expansion'
  assert crass.AST['class']['really_long_class'] == 'really long class with a long expansion'
  assert crass.AST['id']['id with spaces'] == 'spaces'
  assert crass.AST['class']['class with spaces'] == 'spaces'
  