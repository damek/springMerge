from __future__ import division
import sys
import requests
import urllib
from pyPdf import PdfFileWriter, PdfFileReader
import os
import signal
from optparse import OptionParser

downloadInterrupted = "downloadInterrupted"

class IamFromMozillaOpener(urllib.FancyURLopener):
    version = "Mozilla 5.0"

def download(URLList, startingIndex):
    #download PDFs
    numPDFs = len(URLList)
    URLList = URLList[startingIndex:]
    i = startingIndex
    downloader = IamFromMozillaOpener()
    for URL in URLList:
        f = open(downloadInterrupted, 'w')
        f.write(str(i))
        f.close()
        print "Downloading " + str(i+1) + " of " + str(numPDFs) + "."
        downloader.retrieve ("http://www.springerlink.com" + URL, str(i) + ".pdf")
        i = i+1
    f = open(downloadInterrupted, 'w')
    f.write(str(i))
    f.close()
        
def append_pdf(input,output):
    [output.addPage(input.getPage(page_num)) for page_num in range(input.numPages)]
 
def mergePDFs(PDFList, outputFileName):
    #merge all the PDFs in the current list
    output = PdfFileWriter()
    for names in PDFList:
        append_pdf(PdfFileReader(file(names, "rb")), output)
    os.chdir('..')
    outputStream = file(outputFileName, "wb")
    output.write(outputStream)
    outputStream.close()

def findPDFs(pageContents):
    #find all the PDFs on the page
    URLList = []
    currentPos = 0
    currentPos = findNextPDF(pageContents, currentPos, URLList)
    while currentPos != -1:
        currentPos = findNextPDF(pageContents, currentPos, URLList)
    return URLList
        
def findNextPDF(pageContents, currentPos, URLList):
    #find the next pdf on the page
    if currentPos == 0:
        xEnd = pageContents.find("front-matter.pdf", currentPos)
        xEnd = xEnd + len("front-matter.pdf")
        xBegin = pageContents.find("href", xEnd - 100)
        xBegin = xBegin + len('href="')
        URLList.append(pageContents[xBegin:xEnd])
        currentPos = xEnd
    else:
        xEnd = pageContents.find("fulltext.pdf", currentPos)
        if (xEnd != -1):
            xEnd = xEnd + len("fulltext.pdf")
            xBegin = pageContents.find("href", xEnd - 100)
            xBegin = xBegin + len('href="')
            URLList.append(pageContents[xBegin:xEnd])
            currentPos = xEnd
        else:
            xEnd = pageContents.find("back-matter.pdf", currentPos)
            if (xEnd != -1):
                xEnd = xEnd + len("back-matter.pdf")
                xBegin = pageContents.find("href", xEnd - 100)
                xBegin = xBegin + len('href="')
                URLList.append(pageContents[xBegin:xEnd])
                currentPos = xEnd
            else:
                currentPos = -1
    return currentPos

def makeTempFolderName(outputFileName):
    xEnd = len(outputFileName) - outputFileName[::-1].find(".") - 1;
    return outputFileName[:xEnd]

def makeAndChangeDirectory(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)
        os.chdir(dirName)
        f = open(downloadInterrupted, 'w')
        f.write(str(0))
        f.close()
        return 0
    else:
        print "Resuming download of " + dirName
        os.chdir(dirName)
        f = open(downloadInterrupted, 'r')
        startingIndex = int(f.read())
        f.close()
        return startingIndex

def deleteChapters(PDFList, dirName):
    os.chdir(dirName)
    for pdf in PDFList:
        os.remove(pdf)
    os.remove(downloadInterrupted)
    os.chdir('..')
    os.rmdir(dirName)

def getBookTitle(pageContents):
    xBegin = pageContents.find("Link to Book")
    xBegin = xBegin + len('Link to Book">')
    xEnd = pageContents.find('<', xBegin)
    return pageContents[xBegin:xEnd]

def getBookAuthor(pageContents):
    xBegin = pageContents.find("View content where Author is")
    xBegin = xBegin + len("View content where Author is ")
    xEnd = pageContents.find('"', xBegin)
    return pageContents[xBegin:xEnd]

def getBookPublicationDate(pageContents):
    xEnd = pageContents.find('<span class="doi">')
    xBegin = xEnd - 4
    return pageContents[xBegin:xEnd]

def getPageContents(URL):
    response = requests.get(URL)
    return response.text
    
def begin(pageContents, outputFileName, startingIndex):
    #chain all functions together.
    print "Finding PDFs..."
    URLList = findPDFs(pageContents)
    print "Downloading PDFs..."
    download(URLList, startingIndex)
    PDFList = [str(i) + ".pdf" for i in range(0, len(URLList))]
    print "Merging PDFs..."
    dirName = makeTempFolderName(outputFileName)
    mergePDFs(PDFList, outputFileName)
    deleteChapters(PDFList, dirName)
    print "Done!"
    print "Successfully downloaded " + dirName + " to: "
    print os.getcwd() + "/" + dirName + ".pdf"

#!/usr/bin/env python
def signal_handler(signal, frame):
        print 'Downloading interrupted! Run the program again to resume downloading.'
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def formatFileName(pageContents, format):
    title = getBookTitle(pageContents)
    author = getBookAuthor(pageContents)
    year = getBookPublicationDate(pageContents)
    outputFileName = ""
    for e in format:
        if e not in ["T", "A", "Y"]:
            outputFileName = outputFileName + e
        elif e == "T":
            outputFileName = outputFileName + title
        elif e == "A":
            outputFileName = outputFileName + author
        else:
            outputFileName = outputFileName + year
    print outputFileName
    return outputFileName
    
def main():
    parser = OptionParser()
    parser.add_option("-f", "--format", dest="format",
                  help="Format of output file title: T, A (Y) is Title, Author (Year).", metavar="FORMAT")
    parser.add_option("-d", "--directory", dest="directory",
                  help="Directory to save PDF in.", metavar="DIRECTORY")
    (options, args) = parser.parse_args()
    print options.format
    if len(sys.argv) < 2:
        print "USAGE: python SPRINGERLINK_URL SAVE_DIRECTORY (optional) --format='FORMAT' (optional)"
    else:
        if len(options.directory) > 0:
            os.chdir(os.path.expanduser(options.directory))
        URL = sys.argv[1]
        pageContents = getPageContents(URL)
        outputFileName = ""
        if (len(options.format) > 0):
            outputFileName = formatFileName(pageContents, options.format) + ".pdf"
        else:
            outputFileName = formatFileName(pageContents, "T, A (Y)") + ".pdf"
        startingIndex = makeAndChangeDirectory(makeTempFolderName(outputFileName))
        begin(pageContents, outputFileName, startingIndex)
 
if __name__ == "__main__":
    main()

