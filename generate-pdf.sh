#!/bin/bash
set -e # Exit with nonzero exit code if anything fails

# Pull requests and commits to other branches shouldn't try to deploy, just build to verify
if [[ ( "$GITHUB_EVENT_NAME" != "push" ) || ( "$CURRENT_BRANCH" != "$DEFAULT_BRANCH" ) ]]; then
    echo "Skipping pdf generation."
    exit 0
fi

sudo apt-get install -y texlive texlive-lang-cyrillic texlive-latex-extra python-pygments ghostscript

# Generate tex file
bash format-document.sh > document.tex

# Generate pdf
latex -shell-escape document.tex
makeindex document
latex -shell-escape document.tex
dvipdf document.dvi document.pdf
dvips document.dvi

# Copy pdf to publish location (with be used in the next script)
mkdir _site
cp document.pdf "_site/Platform.$REPOSITORY_NAME.pdf"

# Clean up
rm document.tex
rm document.dvi
rm document.pdf
