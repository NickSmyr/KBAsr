import codecs
import os.path
import sys
import shutil


def convert_iso_to_utf(sourceFileName):
    BLOCKSIZE = 1048576  # or some other, desired size in bytes
    with codecs.open(sourceFileName, "r", "ISO-8859-1") as sourceFile:
        with codecs.open(sourceFileName + ".converted", "w", "utf-8") as targetFile:
            while True:
                contents = sourceFile.read(BLOCKSIZE)
                if not contents:
                    break
                targetFile.write(contents)
    shutil.move(
        sourceFileName + ".converted",
        os.path.join("", os.path.basename(sourceFileName)),
    )


convert_iso_to_utf(sys.argv[1])
