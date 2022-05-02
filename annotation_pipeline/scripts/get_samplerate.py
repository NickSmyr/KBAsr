# Returns the samplerate of an input file
import sys
import soundfile

infile = sys.argv[1]
w, sp = soundfile.read(infile)
print(sp)
