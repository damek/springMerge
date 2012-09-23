springMerge
===========

A short python script to merge SpringerLink PDFs. 

Note that this script will only work if your current internet connection gives you access to SpringerLink.  This includes off campus VPN connections to many universities.

Usage: 
===========

print "USAGE: python SPRINGERLINK_URL SAVE_DIRECTORY (optional)"

Example:

python springMerge.py http://www.springerlink.com/content/978-0-387-21718-5 ~/

Will save Mathematical Statistics, Jun Shao (2003).pdf to your home directory on a linux machine.

Features:
===========

1. Automatically names files with the following format:

Title, Author Name (Year).pdf

2. If the program exits mid-download, you can resume downloading by running it again with the same url.