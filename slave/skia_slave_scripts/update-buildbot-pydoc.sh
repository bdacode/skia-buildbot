#!/bin/bash
#
# Runs Epydoc on buildbot code and stores its results in the skia-autogen repo,
# so that they can be browsed at
# http://skia-autogen.googlecode.com/svn/buildbot-docs/index.html
#
# The BUILDBOT_PYDOC_TEMPDIR env variable is the working directory within which
# we will check out the code and generate PyDoc.
#
# Sample Usage:
#  export BUILDBOT_PYDOC_TEMPDIR=/tmp/buildbot-docs
#  bash update-buildbot-pydoc.sh

# Prepare a temporary dir and check out Skia buildbot and docs.
BUILDBOT_PYDOC_TEMPDIR=${BUILDBOT_PYDOC_TEMPDIR:-/tmp/buildbot-docs}

mkdir -p $BUILDBOT_PYDOC_TEMPDIR
cd $BUILDBOT_PYDOC_TEMPDIR

if [ -d "buildbot" ]; then
  pushd buildbot
  git pull
  git checkout origin/master
  popd
else
  git clone https://skia.googlesource.com/buildbot.git
fi
if [ -d "buildbot-docs" ]; then
  svn update --accept theirs-full buildbot-docs
else
  svn checkout https://skia-autogen.googlecode.com/svn/buildbot-docs  # writeable
fi

# Run Epydoc.
cd buildbot
epydoc --graph classtree --parse-only --docformat plaintext scripts \
site_config master slave -o ../buildbot-docs

ret_code=$?
if [ $ret_code != 0 ]; then
  echo "Error while executing Epydoc command"
  exit $ret_code
fi

cd ../buildbot-docs

# Remove the date and timestamp from footer in Pydocs.
perl -pi -e 's/Generated by Epydoc (\d+\.\d+\.\d+) .*/Generated by Epydoc $1/' *

# Add any newly created files to Subversion.
NEWFILES=$(svn status | grep ^\? | awk '{print $2}')
if [ -n "$NEWFILES" ]; then
  svn add $NEWFILES
fi

# If there are no changes exit. (We'll wait until there are any actual doc
# changes before updating the timestamp and committing changes to the
# repository.)
MODFILES=$(svn status | grep ^[AM])
if [ -z "$MODFILES" ]; then
  echo "No documentation updates, exiting early."
  exit 0
fi

# Make sure that all files have the correct mimetype.
find . -name '*.html' -exec svn propset svn:mime-type text/html '{}' \;
find . -name '*.css'  -exec svn propset svn:mime-type text/css '{}' \;
find . -name '*.js'   -exec svn propset svn:mime-type text/javascript '{}' \;
find . -name '*.gif'  -exec svn propset svn:mime-type image/gif '{}' \;
find . -name '*.png'  -exec svn propset svn:mime-type image/png '{}' \;

# Output files with documentation updates.
echo -e "\n\nThe following are the documentation updates:"
echo $MODFILES

