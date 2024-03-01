class HEP:

    def __init__(self, srcFile, minOcp):
        # path to source file
        self.__srcFile = srcFile
        # minimum occupancy threshold
        self.__minOcp = minOcp
        # high occupancy itemsets
        self.__HOIs = dict()
    
    def __getUBO(self, STSet):
        # scan support transaction set
        lenList = dict()
        for trans in STSet:
            length = trans[1]
            if length not in lenList:
                lenList[length] = 0
            lenList[length] += 1
        
        # calculate upper-bound occupancy
        l = list(sorted(lenList.keys()))
        maxUBO = 0
        for x in range(len(l)):
            lx = l[x]
            UBO = 0
            for i in range(x, len(l)):
                li = l[i]
                UBO += lenList[li] * (lx / li)
            if UBO > maxUBO:
                maxUBO = UBO
        return maxUBO
    
    def __getOcp(self, itemset, STSet):
        ocp = 0
        for trans in STSet:
            ocp += len(itemset) / trans[1]
        return ocp
    
    def run(self):
        # scan database to obtain occupancy-list of each 1-itemset
        ocpList = dict()
        maxT = 0
        with open(self.__srcFile, 'r') as file:
            i = 0
            for line in file:
                trans = line.split()
                if len(trans) > maxT:
                    maxT = len(trans)
                for item in trans:
                    item = tuple([item])
                    if item not in ocpList:
                        ocpList[item] = set()
                    ocpList[item].add((i, len(trans)))
                i += 1
            self.__minOcp *= i
        print(maxT)
        # mine 1-itemsets
        C1 = dict()
        for P in ocpList:
            STSetP = ocpList[P]
            if len(STSetP) >= self.__minOcp:
                UBO = self.__getUBO(STSetP)
                if UBO >= self.__minOcp:
                    C1[P] = STSetP
                    ocp = self.__getOcp(P, STSetP)
                    if ocp >= self.__minOcp:
                        self.__HOIs[P] = ocp
        
        # mine k-itemsets
        k = 2
        while len(C1) > 1:
            C = dict()
            checked = set()
            for P1 in C1:
                for P2 in C1:
                    P = tuple(sorted(set(P1).union(P2)))
                    if len(P) == k and P not in checked:
                        STSetP = C1[P1].intersection(C1[P2])
                        if len(STSetP) >= self.__minOcp:
                            UBO = self.__getUBO(STSetP)
                            if UBO >= self.__minOcp:
                                C[P] = STSetP
                                ocp = self.__getOcp(P, STSetP)
                                if ocp >= self.__minOcp:
                                    self.__HOIs[P] = ocp
                        checked.add(P)
            C1 = C
            k += 1
    
    def export(self, desFile):
        with open(desFile, 'w') as file:
            for key, val in self.__HOIs.items():
                text = '{} {:.2f}\n'.format(key, val)
                file.write(text)