import sys, os, re, shutil, errno, subprocess, filecmp

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
AST = {
  'id':    {},
  'class': {}
}

################################################################################
# Logging

# Logging symbols
FATAL   = '[!]' # Fatal: something has gone really wrong
WARN    = '[#]' # Warning: not critical, but there is still something wrong
NORMAL  = '[:]' # Normal: regular output for updates and progress
FOUND   = '[@]' # Found: found a file

# Log to the console
def log(string, label=NORMAL):
  print(label + ' ' + string)

################################################################################
# File utilities

# Take a path and examine all of it's contents recursively for files
# that end with a specific extension and return a list of those paths
def analyzeDir(path, extension):

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

  # Alert to user if there is anything to do
  if filelist:
    log('Found targets: ' + ', '.join(filelist), FOUND)
  else:
    log('No targets found', WARN)

  return filelist

# Copy contents of one file to another file or directory
# and create the outfile if it doesn't exist
def copyfile(infile, outfile):

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

# Build an AST from the crassfile, which is just a dictionary that links 1:1 between the alias and their expansion
def buildAST(crassfile):

  with open(crassfile) as file:
    for line in file:

      # Ignore comments or empty lines
      if line.startswith('//') or line == '\n':
        continue

      else:

        try:

          # Split line at the equals sign and strip trailing whitespace
          alias, expansion = line.split('=')
          alias, expansion = alias.strip(), expansion.strip()

          # Classify into IDs and Classes, then update the AST accordingly
          if alias.startswith('.'):
            AST['class'][alias[1:]] = expansion
          elif alias.startswith('#'):
            AST['id'][alias[1:]] = expansion
          else:
            raise SyntaxError('Line does not appear to have a proper assignment between alias and expansion')

        except ValueError:
          raise SyntaxError('Line does not look like a proper crass alias definition. You might be missing a = or forgot to comment out this line.')

# Parse a list of html files for instances of "class=''" and "id=''"
def parse(filelist):

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
        
        # Get contents of "id=''"
        ids = re.findall(r'id\s*=\s*[\"\']\s*(.*?)\s*[\"\']', line, re.DOTALL)

        # If there are classes declared on this line...
        if classes:
          
          # ... Iterate over them and compare it to our AST
          # Then replace if they are present
          for c in classes:
            if c in AST['class']:
              replace(c, AST['class'][c], path, cfg['build'] + path)
              replaced = True

        # If there are ids declared on this line
        if ids:
          
          # ... Iterate over them and compare it to our AST
          # Then replace if they are present
          for i in ids:
            if i in AST['id']:
              replace(i, AST['id'][i], path, cfg['build'] + path)
              replaced = True

    # If no matches, still copy the file to build
    if not replaced:
      copyfile(path, cfg['build'] + path)

################################################################################
# Replacer

# Replace all instances of instance in infile with replacement
def replace(instance, replacement, infile, outfile):

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

  if not isinstance(args, list):
    raise TypeError('Argument to must be a list.')
  if len(args) != 4:
    usage()
    raise IndexError('Improper number of arguments given, refer to usage above.')

  # Get source directory
  cfg['src'] =   args[1]

  # Get crass file
  cfg['crass'] = args[2]

  # Get build directory
  cfg['build'] = args[3]

  # Error Handling
  log('Making sure directories aren\'t nested...')

  # Make sure no folders are nested in each other
  dirs = [cfg['src'], cfg['crass'], cfg['build']]
  for outerdir in dirs:
    for innerdir in dirs:

      if outerdir != innerdir:
        if os.path.realpath(outerdir).startswith(os.path.realpath(innerdir)):
          raise OSError(outerdir + ' is inside ' + innerdir + '. Un-nest directories and try again.')

# Display how the program is intended to be used
def usage():
  print('USAGE: swan.py <source directory> <crass file> <output directory>')

################################################################################
# Main

if __name__ == '__main__':

  # Take inputs from commandline
  cli()

  # Build an AST of aliases from the crassfile, check for errors
  buildAST(cfg['crass'])

  # Analyze a directory for html files.
  # Copy all non-html files to build directory
  htmllist = analyzeDir(cfg['src'], '.html')

  # Parse all html files and replace any contents that align with our aliases
  parse(htmllist)
