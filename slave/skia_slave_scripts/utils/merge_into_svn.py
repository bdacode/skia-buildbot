#!/usr/bin/env python
# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Commit all files within a directory to an SVN repository.

To test:
  cd .../buildbot/slave/skia_slave_scripts/utils
  echo "SvnUsername" >../../../site_config/.svnusername
  echo "SvnPassword" >../../../site_config/.svnpassword
  rm -rf /tmp/svn-source-dir
  mkdir -p /tmp/svn-source-dir
  date >/tmp/svn-source-dir/date.png
  date >/tmp/svn-source-dir/date.txt
  CR_BUILDBOT_PATH=../../../third_party/chromium_buildbot
  PYTHONPATH=$CR_BUILDBOT_PATH/scripts:$CR_BUILDBOT_PATH/site_config \
   python merge_into_svn.py \
   --source_dir_path=/tmp/svn-source-dir \
   --merge_dir_path=/tmp/svn-merge-dir \
   --dest_svn_url=https://skia-autogen.googlecode.com/svn/gm-actual/test \
   --svn_username_file=.svnusername --svn_password_file=.svnpassword
  # and check
  #  http://code.google.com/p/skia-autogen/source/browse/#svn%2Fgm-actual%2Ftest

"""

import misc
import optparse
import os
import shutil
import sys
import tempfile

from common import chromium_utils
from slave import svn


SUBDIRS_TO_IGNORE = ['.git', '.svn', 'third_party']
FILES_CHUNK = 50


def ReadFirstLineOfFileAsString(filename):
  """Safely return the first line of a file as a string.
  If there is an exception, it will be raised to the caller, but we will
  close the file handle first.

  @param filename path to the file to read
  """
  f = open(filename, 'r')
  try:
    contents = f.readline().splitlines()[0]
  finally:
    f.close()
  return contents


def _CopyAllFiles(source_dir, dest_dir):
  """Copy all files from source_dir into dest_dir.

  Recursively copies files from directories as well.
  Skips directories specified in SUBDIRS_TO_IGNORE.

  @param source_dir
  @param dest_dir
  """
  basenames = os.listdir(source_dir)
  for basename in basenames:
    source_path = os.path.join(source_dir, basename)
    dest_path = os.path.join(dest_dir, basename)
    if basename in SUBDIRS_TO_IGNORE:
      continue
    if os.path.isdir(source_path):
      if not os.path.isdir(dest_path):
        os.makedirs(dest_path)
      _CopyAllFiles(source_path, dest_path)
    else:
      shutil.copyfile(source_path, dest_path)


def _DeleteDirectoryContents(directory):
  """Delete all contents (recursively) within dir, but don't delete the
  directory itself.

  @param dir directory whose contents to delete
  """
  basenames = os.listdir(directory)
  for basename in basenames:
    path = os.path.join(directory, basename)
    if os.path.isdir(path):
      chromium_utils.RemoveDirectory(path)
    else:
      os.unlink(path)


# TODO: We should either add an Update() command to svn.py, or make its
# _RunSvnCommand() method public; in the meanwhile, abuse its private
# _RunSvnCommand() method.
# See https://code.google.com/p/skia/issues/detail?id=713
def _SvnUpdate(repo, additional_svn_flags=None):
  if not additional_svn_flags:
    additional_svn_flags = []
  # pylint: disable=W0212
  return repo._RunSvnCommand(['update'] + additional_svn_flags)


# TODO: We should either add an Import() command to svn.py, or make its
# _RunSvnCommand() method public; in the meanwhile, abuse its private
# _RunSvnCommand() method.
# See https://code.google.com/p/skia/issues/detail?id=713
def _SvnImport(repo, path, url, message, additional_svn_flags=None):
  if not additional_svn_flags:
    additional_svn_flags = []
  # pylint: disable=W0212
  return repo._RunSvnCommand(['import', path, url, '--message', message]
                             + additional_svn_flags)


# TODO: We should either add a command like this to svn.py, or make its
# _RunSvnCommand() method public; in the meanwhile, abuse its private
# _RunSvnCommand() method.
# See https://code.google.com/p/skia/issues/detail?id=713
def _SvnDoesUrlExist(repo, url):
  try:
    # pylint: disable=W0212
    repo._RunSvnCommand(['ls', url])
    return True
  except Exception:
    # TODO: this will treat *any* exception in "svn ls" as signalling that
    # the URL does not exist.  Should we look for something more specific?
    return False


# TODO: We should either add a command like this to svn.py, or make its
# _RunSvnCommand() method public; in the meanwhile, abuse its private
# _RunSvnCommand() method.
# See https://code.google.com/p/skia/issues/detail?id=713
def _SvnCleanup(repo):
  # pylint: disable=W0212
  repo._RunSvnCommand(['cleanup'])


def MergeIntoSvn(options):
  """Update an SVN repository with any new/modified files from a directory.

  @param options struct of command-line option values from optparse
  """
  # Get path to SVN username and password files.
  # (Patterned after slave_utils.py's logic to find the .boto file.)
  site_config_path = os.path.join(misc.BUILDBOT_PATH, 'site_config')
  svn_username_path = os.path.join(site_config_path, options.svn_username_file)
  svn_password_path = os.path.join(site_config_path, options.svn_password_file)
  if not (os.path.isfile(svn_username_path)
          and os.path.isfile(svn_password_path)):
    raise Exception(
      'Skipping MergeIntoSvn step: missing username or password file.\n'
      '  username file: %s\n  password file: %s\n' % (
        os.path.abspath(svn_username_path), os.path.abspath(svn_password_path)))
  svn_username = ReadFirstLineOfFileAsString(svn_username_path).rstrip()
  svn_password = ReadFirstLineOfFileAsString(svn_password_path).rstrip()

  # Check out the SVN repository into the merge dir.
  # (If no merge dir was specified, use a temporary dir.)
  if options.merge_dir_path:
    mergedir = options.merge_dir_path
  else:
    mergedir = tempfile.mkdtemp()
  if not os.path.isdir(mergedir):
    os.makedirs(mergedir)
  repo = svn.Svn(directory=mergedir,
                 username=svn_username, password=svn_password,
                 additional_svn_flags=[
                     '--trust-server-cert', '--no-auth-cache',
                     '--non-interactive'])

  # If this repo hasn't been created yet, create it, and clear out the mergedir
  # (just in case there is old stuff in there) to match the newly created repo.
  if not _SvnDoesUrlExist(repo=repo, url=options.dest_svn_url):
    _DeleteDirectoryContents(mergedir)
    print _SvnImport(
        repo=repo, url=options.dest_svn_url, path='.',
        message='automatic initial creation by merge_into_svn.py')

  # If we have already checked out this workspace, just update it (resolving
  # any conflicts in favor of the repository HEAD) rather than pulling a
  # fresh checkout.
  if os.path.isdir(os.path.join(mergedir, '.svn')):
    try:
      print _SvnUpdate(repo=repo,
                       additional_svn_flags=['--accept', 'theirs-full'])
    except Exception as e:
      if 'doesn\'t match expected UUID' in ('%s' % e):
        # We occasionally have to reset the repository due to space constraints.
        # In this case, the UUID will change and we have to check out again.
        # Bug: http://code.google.com/p/skia/issues/detail?id=792
        # First, clear the existing directory
        print 'The remote repository UUID has changed.  Removing the existing \
              checkout and checking out again to update with the new UUID'
        chromium_utils.RemoveDirectory(mergedir)
        os.makedirs(mergedir)
        # Then, check out the repo again.
        print repo.Checkout(url=options.dest_svn_url, path='.')
      elif 'svn cleanup' in ('%s' % e):
        # If a previous commit did not go through, we sometimes end up with a
        # locked working copy and are unable to update.  In this case, run
        # svn cleanup.
        _SvnCleanup(repo)
        print _SvnUpdate(repo=repo,
                         additional_svn_flags=['--accept', 'theirs-full'])
      else:
        raise e
  else:
    print repo.Checkout(url=options.dest_svn_url, path='.')

  # Copy in all the files we want to update/add to the repository.
  _CopyAllFiles(source_dir=options.source_dir_path, dest_dir=mergedir)

  # Make sure all files are added to SVN and have the correct properties set.
  new_files = repo.GetNewFiles()
  for new_file in new_files:
    # Add one file at a time, because otherwise Windows can choke on a command
    # line that's too long (if there are lots of files).
    repo.AddFiles([new_file])

  # Set required svn properties on certain file extensions.
  _SetProperty(_FindFiles(mergedir, '.html'), 'svn:mime-type',
               'text/html', repo)
  _SetProperty(_FindFiles(mergedir, '.css'), 'svn:mime-type', 'text/css', repo)
  _SetProperty(_FindFiles(mergedir, '.js'), 'svn:mime-type',
               'text/javascript', repo)
  _SetProperty(_FindFiles(mergedir, '.json'), 'svn:mime-type',
               'text/x-json', repo)
  _SetProperty(_FindFiles(mergedir, '.gif'), 'svn:mime-type', 'image/gif', repo)
  _SetProperty(_FindFiles(mergedir, '.png'), 'svn:mime-type', 'image/png', repo)
  _SetProperty(_FindFiles(mergedir, '.pdf'), 'svn:mime-type',
               'application/pdf', repo)
  _SetProperty(_FindFiles(mergedir, '.cpp'), 'svn:eol-style', 'LF', repo)
  _SetProperty(_FindFiles(mergedir, '.h'), 'svn:eol-style', 'LF', repo)
  _SetProperty(_FindFiles(mergedir, '.c'), 'svn:eol-style', 'LF', repo)
  _SetProperty(_FindFiles(mergedir, '.gyp'), 'svn:eol-style', 'LF', repo)
  _SetProperty(_FindFiles(mergedir, '.gypi'), 'svn:eol-style', 'LF', repo)

  # Commit changes to the SVN repository and clean up.
  print repo.Commit(message=options.commit_message)
  if not options.merge_dir_path:
    print 'deleting mergedir %s' % mergedir
    chromium_utils.RemoveDirectory(mergedir)
  return 0


def _SetProperty(files, property_name, property_value, repo):
  """Calls repo.SetProperty() with some special handling.

  The special handling needed by merge_into_svn is:

  -  Split up the file array into chunks no longer than FILES_CHUNK so that we
     don't run into http://code.google.com/p/skia/issues/detail?id=582
     ('buildbot UploadGMResults step failing: "The command line is too long"')
  """
  for files_chunk in _GetChunks(files, FILES_CHUNK):
    repo.SetProperty(files_chunk, property_name, property_value)


def _GetChunks(seq, n):
  """"Yield successive n-sized chunks from the specified sequence."""
  for i in xrange(0, len(seq), n):
    yield seq[i:i+n]


def _FindFiles(root, file_pattern):
  """Finds all files below the specified dir that match the pattern."""
  ret_files = []
  for directory, _subdirs, files in os.walk(root):
    for subdir_to_ignore in SUBDIRS_TO_IGNORE:
      if subdir_to_ignore in directory:
        break
    else:
      for filename in files:
        if filename.endswith(file_pattern):
          svn_file = os.path.join(directory, filename)
          if svn_file.startswith(root):
            svn_file = svn_file[len(root) + 1:]
          ret_files.append(svn_file)
  return ret_files


def main(argv):
  option_parser = optparse.OptionParser()
  option_parser.add_option(
      '--commit_message', default='merge_into_svn automated commit',
      help='message to log within SVN commit operation')
  option_parser.add_option(
      '--dest_svn_url',
      help='URL pointing to SVN directory where we want to commit the files')
  option_parser.add_option(
      '--merge_dir_path',
      help='path within which to make a local checkout and merge contents;'
           ' if this directory already contains a checkout of the SVN repo,'
           ' it will be updated (rather than a complete fresh checkout pulled)'
           ' to speed up the merge process.'
           ' If this option is not specified, a temp directory will be created'
           ' and a complete fresh checkout will be pulled')
  option_parser.add_option(
      '--source_dir_path',
      help='full path of the directory whose contents we wish to commit')
  option_parser.add_option(
      '--svn_password_file',
      help='file (within site_config dir) from which to read the SVN password')
  option_parser.add_option(
      '--svn_username_file',
      help='file (within site_config dir) from which to read the SVN username')
  (options, args) = option_parser.parse_args()
  if len(args) != 0:
    raise Exception('bogus command-line argument; rerun with --help')
  misc.ConfirmOptionsSet({
      '--dest_svn_url': options.dest_svn_url,
      '--source_dir_path': options.source_dir_path,
      '--svn_password_file': options.svn_password_file,
      '--svn_username_file': options.svn_username_file,
      })
  return MergeIntoSvn(options)


if '__main__' == __name__:
  sys.exit(main(None))
