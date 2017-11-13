import sys, os, re, shutil, errno, subprocess, filecmp

# Check for pytest
try:
  import pytest
except ImportError:
  print('Warning: Pytest isn\'t installed. This will not affect crass, however you will not be able to run the tests.')

################################################################################
# Global Data

# Store user cmdline args
cfg = {
  'src':   './?', # Location of source directory
  'crass': './?', # Location of crass file to apply to source directory
  'build': './?', # Location of where to put crass'd files
}

# Store the crass abstract syntax tree
# Essentially just hold all ID elements in one branch and all classes in another,
# those branches then hold the 1:1 connection between aliases and their expansions
AliasDict = {}

################################################################################
# Logging

# Logging symbols
FATAL   = '[!]' # Fatal: something has gone really wrong
WARN    = '[#]' # Warning: not critical, but there is still something wrong
NORMAL  = '[:]' # Normal: regular output for updates and progress
FOUND   = '[@]' # Found: found a file

def log(string, label=NORMAL):
  ''' Log to the console '''
  print(label + ' ' + string)

################################################################################
# File utilities

def analyzeDir(path, extension):
  ''' Take a path and examine all of it's contents recursively for files
  that end with a specific extension and return a list of those paths '''

  # Recursively analyze the directory for HTML files
  filelist = []

  # Walk the source directory and analyze all files
  for root, subdirs, files in os.walk(path):

    for filename in files:

      # Form a proper path to the file
      path = os.path.join(root, filename)

      # Get files with proper extension
      if filename.endswith(extension):
        filelist.append(path)

      # Other files can be preserved, however
      else:
        copyfile(path, cfg['build'] + path)

  return filelist

def copyfile(infile, outfile):
  ''' Copy contents of one file to another file or directory
  and create the outfile if it doesn't exist '''

  # Check to see if infile is a directory that doesn't exist
  if not os.path.exists(os.path.dirname(outfile)):

    # If it doesn't exist, make the file, then copy
    # the contents from infile to it
    try:
      os.makedirs(os.path.dirname(outfile))
      shutil.copy(infile, outfile)  
    except OSError as exc:
      if exc.errno != errno.EEXIST:
        raise
  
  # If outfile isn't a directory, and the outfile doesn't exist, 
  # copy infile to that location
  elif not os.path.isfile(outfile):
    shutil.copy(infile, outfile)

################################################################################
# Parsers

def buildAliasDict(crassfile):
  ''' Build an AliasDict from the crassfile, which is just a dictionary 
  that links the alias to it's expansion '''

  with open(crassfile) as file:
    for i, line in enumerate(file):

      # Ignore comments or empty lines
      if line.startswith('//') or line in ['\n', '', None]:
        continue
      else:

        try:
          # Split line at the equals sign and strip trailing whitespace
          alias, expansion = line.split('=')
        except ValueError:
          raise ValueError('Error Building AliasDict: Missing = on line ' + str(i + 1))

        alias, expansion = alias.strip(), expansion.strip()

        # Classify into IDs and Classes, then update the alias dict accordingly
        if alias.startswith('.'):
          alias = alias[1:]

        # Add alias
        AliasDict[alias] = expansion

def parse(filelist):
  ''' Parse a list of html files for instances of `class=` '''

  log('Parsing targets...')

  for path in filelist:

    # Keep track if we found matches or not, since as of this point
    # the html file isn't copied to the build directory.
    # If we don't find any matches, copy the file to build without
    # replacing
    replaced = False

    with open(path, 'r') as file:

      for line in file:

        # Regex classes and ids

        # Get contents of "class=''"
        classes = re.findall(r'class\s*=\s*[\"\']\s*(.*?)\s*[\"\']', line, re.DOTALL)
        
        # If there are classes declared on this line...
        if classes:
          
          # ... Iterate over them and compare it to our AliasDict
          # Then replace if they are present
          for c in classes:
            if c in AliasDict:
              replace(c, AliasDict[c], path, cfg['build'] + path)
              replaced = True

    # If no matches, still copy the file to build
    if not replaced:
      copyfile(path, cfg['build'] + path)

################################################################################
# Replacer

def replace(instance, replacement, infile, outfile):
  ''' Replace all instances of `instance` in `infile` with `replacement` '''

  log('Searching for instances of ' + instance + ' in ' + infile)

  # Copy infile to outfile and create outfile if it doesn't exist
  copyfile(infile, outfile)

  html_content = ''

  with open(outfile, 'r+') as file:
    for line in file:

      # Make sure what we want to replace is in a tag, we don't
      # want to override a users data that could potentially be the same
      # as their css elements
      within_tag = re.findall(r'<\s*(.*?)\s*>', line, re.DOTALL)
      if within_tag:
        html_content += line.replace(instance, replacement)
      else:
        html_content += line

    # Write data
    file.seek(0)
    file.truncate()
    file.write(html_content)

################################################################################
# CLI

# Handle arguments
def cli(args):
  ''' Interface with argv or any list of arguments to gather file locations '''

  if not isinstance(args, list):
    raise TypeError('Argument to must be a list.')
  if len(args) != 4:
    usage()
    raise IndexError('Improper number of arguments given, refer to usage above.')

  # Make sure we aren't getting weird types
  for arg in args:
    if not isinstance(arg, str):
      raise TypeError('Argument ' + str(arg) + ' is not a string!')

  cfg['src'], cfg['crass'], cfg['build'] = args[1], args[2], args[3]

  # Error Handling
  log('Making sure directories aren\'t nested...')

  # Make sure no folders are nested in each other
  dirs = [cfg['src'], cfg['crass'], cfg['build']]
  for outerdir in dirs:
    for innerdir in dirs:

      if outerdir != innerdir:
        if os.path.realpath(outerdir).startswith(os.path.realpath(innerdir)):
          raise OSError(outerdir + ' is inside ' + innerdir + '. Un-nest directories and try again.')

def usage():
  ''' Display how the program is intended to be used '''
  print('USAGE: crass.py <source directory> <crassfile> <output directory>')

################################################################################
# Main

if __name__ == '__main__':

  # Take inputs from commandline
  cli(sys.argv)

  # Build an AliasDict of aliases from the crassfile, check for errors
  buildAliasDict(cfg['crass'])

  # Analyze a directory for html files.
  # Copy all non-html files to build directory
  htmllist = analyzeDir(cfg['src'], '.html')

  # Parse all html files and replace any contents that align with our aliases
  parse(htmllist)

################################################################################
# Tests

# Test the function inputs
def test_cli_arguments():
  ''' Test to see if the CLI is functioning as intended '''

  # Too many/few arguments
  with pytest.raises(TypeError):
    cli(['0', '1'], ['2', '3'])
    cli()

  # Check to see if argument is a list
  with pytest.raises(TypeError):
    cli("string")
    cli(1)
    cli(True)

  # Check list length
  with pytest.raises(IndexError):
    cli([])
    cli(['0'])
    cli(['0', '1'])
    cli(['0', '1', '2'])
    cli(['0', '1', '2', '3', '4'])

  # Correct list length
  cli(['0', '1', '2', '3'])


# Make sure src and build aren't nested
def test_cli_nested_check():
  ''' Test to see if crass identifies possible recursion problems '''

  # Improper arrangements
  with pytest.raises(OSError):
    cli(['py', './tests/dir_test_one/src', './tests/dir_test_one/crassfile.crass', './tests/dir_test_one/src/build'])
    cli(['py', './tests/dir_test_two/build/src', './tests/dir_test_two/crassfile.crass', './tests/dir_test_two/build'])
  
  # Correct arrangement
  assert cli(['py', './tests/dir_test_three/src', './tests/dir_test_three/crassfile.crass', './tests/dir_test_three/build']) == None

def test_crass_syntax():
  ''' Test to see if crass can identify proper errors
  and read files properly'''

  with pytest.raises(ValueError):
    buildAliasDict('./tests/ast_tests/crass_test_one.crass')
    buildAliasDict('./tests/ast_tests/crass_test_two.crass')

  # Test a proper crassfile
  buildAliasDict('./tests/ast_tests/crass_test_three.crass')
  assert AliasDict['class'] == 'class'
  assert AliasDict['really_long_class'] == 'really long class with a long expansion'
  assert AliasDict['class with spaces'] == 'class with spaces'
  assert AliasDict['no_dot'] == 'no dot'
  assert AliasDict['no dot and spaces'] == 'no dot and spaces'

def test_deployment():
  ''' Test crass by using an example website '''

  # Take inputs from commandline
  cli(['crass.py', './example/src', './example/example.crass', './example/build'])

  # Build an AliasDict of aliases from the crassfile, check for errors
  buildAliasDict(cfg['crass'])

  # Analyze a directory for html files.
  # Copy all non-html files to build directory
  htmllist = analyzeDir(cfg['src'], '.html')

  # Parse all html files and replace any contents that align with our aliases
  parse(htmllist)
  