import codecs
import sys

BLOCKSIZE = 1048576 # or some other, desired size in bytes
sourceFileName = sys.argv[1]
with codecs.open(sourceFileName, "r", "ISO-8859-1") as sourceFile:
    with codecs.open(sourceFileName + ".converted", "w", "utf-8") as targetFile:
        while True:
            contents = sourceFile.read(BLOCKSIZE)
            if not contents:
                break
            targetFile.write(contents)