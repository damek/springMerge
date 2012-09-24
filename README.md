springMerge
===========

A short python script to merge SpringerLink PDFs. 

Note that this script will only work if your current internet connection gives you access to SpringerLink.  This includes off campus VPN connections to many universities.

Features:
===========

1. Automatically names files with the following format: Title, Author Name (Year).pdf

2. If the program exits mid-download, you can resume downloading by running it again with the same url.

Installation
===========

Install pip (http://pypi.python.org/pypi/pip) and then run the following commands:

1. sudo pip install requests

2. sudo pip install pyPdf

Usage: 
===========

USAGE: python SPRINGERLINK_URL --directory="DIRECTORY_TO_SAVE" --format="FORMAT"

format is any combination of the letters $T, $A, and $Y with any other characters.

Example:

python springMerge.py http://www.springerlink.com/content/978-0-387-21718-5 --directory="~/" --format="&T, &A (&Y)"

Will save Mathematical Statistics, Jun Shao (2003).pdf to your home directory on a linux machine.

License:
===========
Any license that gives you permission to modify and redistribute this code however you want.
