from DFHOI import DFHOI
import sys

srcFile = sys.argv[1]
minOcp = sys.argv[2]
desFile = sys.argv[3]

obj = DFHOI(srcFile = srcFile, minOcp = float(minOcp))

obj.run()
obj.export(desFile)