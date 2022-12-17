#!/bin/bash

# Deploy Sphinx documentation system

## @fn setup_docs
setup_docs ()
{
  # Set up the documentation paths on bow account.
  ## Identify project directory
    echo -e "Creating docs directory in bow account..."
    rm -Rf ${BOWDOCS}
    mkdir ${BOWDOCS}
    cp ${WAXDOCS}/README_BOW.md ${BOWDOCS}/README.md
    mkdir ${BOWDOCS}/help
    cp ${WAXDOCS}/help/* ${BOWDOCS}/help
    if [[ -d ${BOWDOCS} &&  -d ${BOWDOCS}/help && -f ${BOWDOCS}/README.md ]]; then
      ls -R ${BOWDOCS}
      step_ok
      return 0
    else
      echo -e "Not able to set up: ${BOWDOCS}"; step_fail
      return 1
    fi
}

## @fn setup_sphinx
setup_sphinx ()
{
  # Set options for Sphinx project:
  ## Set project name, author name and version number
  ## Identify project directory
    echo -e "Running Sphinx quickstart to create sphinx project for BoW.
See: http://www.sphinx-doc.org/en/stable/invocation.html for other options to consider."
    sphinx-quickstart -q -p bow -a GenuineMeritSoftware -v 0.0 -r 7 ${BOWDOCS}/sphinx
    mkdir ${BOWDOCS}/sphinx/source
    cp ${WAXDOCS}/source/conf.py ${BOWDOCS}/sphinx/source
    cp ${WAXDOCS}/source/README.md ${BOWDOCS}/sphinx/source
    cp ${WAXDOCS}/source/*.rst ${BOWDOCS}/sphinx/source

    if [[ -d ${BOWDOCS}/sphinx/source && -f ${BOWDOCS}/sphinx/source/conf.py ]]; then
      tput setaf 6 #teal
      echo -e "Sphinx documentation system installed and source files copied in from GitHub.
  DEV: Still need to define sourcedir, outputdir, filenames.
  For many more options, including sphinx-apidoc for Python, see:
      http://www.sphinx-doc.org/en/stable/invocation.html
  To modify documentation, edit files in ${SPHINX}/source
  To execute a sphinx build:
        cd ${DOCS}/sphinx/source
        sphinx-build -b html"
      ls -R ${BOWDOCS}/sphinx
      tput setaf 7 #white
      step_ok
      return 0
    else
      echo -e "Not able to initialize Sphinx documentationn system."; step_fail
      return 1
    fi
}

## @fn set_owner
set_owner ()
{
  echo -e "Setting owner:group of /home/bow/docs to bow:bow..."
  # Set owner and group of the docs collection to bow
  chown -R bow:bow ${BOWDOCS}
  BOWUSR=$(ls -l ${BOWDOCS}/README.md | awk '{ print $3 }')
  BOWGRP=$(ls -l ${BOWDOCS}/README.md | awk '{ print $3 }')
  if [[ ${BOWUSR} -eq "bow" && ${BOWGRP} -eq "bow" ]]; then
    step_ok
    return 0
  else
    echo -e "Not able to set /docs ownership to bow account"; step_fail
    return 1
  fi
}

## ================= MAIN ===========================
SCRIPT="${WAXPATH}/build/"$(basename -- "$0")
WAXDOCS="${WAXPATH}/docs"
BOWDOCS="/home/bow/docs"
. ${WAXPATH}/build/status.sh

(bash ${WAXPATH}/build/install_status.sh ${SCRIPT}); RC=$?
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if status is OK
setup_docs; RC=$?
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if docs directory created OK
setup_sphinx
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if Sphinx system set up OK
set_owner
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if ownership set to bow OK
echo "${SCRIPT} COMPLETE" >> $TRKPATH
