from ATHOI import ATHOI
import sys

srcFile = sys.argv[1]
numHOIs = sys.argv[2]
desFile = sys.argv[3]

obj = ATHOI(srcFile = srcFile, numHOIs = int(numHOIs))

obj.run()
obj.export(desFile)