from praatio import tgio
from os.path import join, basename



# def parse_lab_file(filename):
#     with open(filename, "r") as f:
#         lines = f.readlines()
#
#     interval_annotations = []
#     for line in lines:
#         start, end, label = line.split()
#         start = float(start)
#         end = float(end)
#         interval_annotations.append(IntervalAnnotation(start, end, label))
#
#     return interval_annotations
#
#
# def parse_textgrid_file(filename):
#
#     tg = tgio.openTextgrid(join(filename))
#     intervals = tg.tierDict["annot"].entryList
#     return [IntervalAnnotation(x.start, x.end, x.label) for x in intervals]
