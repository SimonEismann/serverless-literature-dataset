#!/usr/bin/env python3

import glob
import os

pdfs = glob.glob("pdfs/*.pdf")
for pdf in pdfs:
	os.system("pdftotext {}".format(pdf))
os.system("cat pdfs/*.txt > _tagcloud.txt")
os.system("rm pdfs/*.txt")

print("Written tag cloud source to _tagcloud.txt.")
print("Render with https://www.wordclouds.com/.")

os.system("pdftk pdfs/*.pdf cat output _allpdfs.pdf")
