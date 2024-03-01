class DFHOI:

    def __init__(self, srcFile, minOcp):
        # path to source file
        self.__srcFile = srcFile
        # minimum occupancy threshold
        self.__minOcp = minOcp
        # indicate if all transactions have the same length
        self.__sameLength = True
        # length of transactions
        self.__lenTrans = list()
        # high occupancy itemsets
        self.__HOIs = dict()
    
    def __getUBO(self, STSet):
        # scan support transaction set
        lenList = dict()
        for trans in STSet:
            length = self.__lenTrans[trans]
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
            ocp += len(itemset) / self.__lenTrans[trans]
        return ocp
    
    def __mine1Itemset(self, STSet):
        C1 = dict()
        for P in STSet:
            STSetP = STSet[P]
            if len(STSetP) >= self.__minOcp:
                if not self.__sameLength:
                    UBO = self.__getUBO(STSetP)
                    if UBO >= self.__minOcp:
                        C1[P] = STSetP
                        ocp = self.__getOcp(P, STSetP)
                        if ocp >= self.__minOcp:
                            self.__HOIs[P] = ocp
                else:
                    C1[P] = STSetP
                    ocp = self.__getOcp(P, STSetP)
                    if ocp >= self.__minOcp:
                        self.__HOIs[P] = ocp
        return C1
    
    def __mineDepth(self, C):
        itemsets = list(C.keys())
        for i in range(len(itemsets)):
            Ck = dict()
            P1 = itemsets[i]
            for j in range(i+1, len(itemsets)):
                P2 = itemsets[j]
                STSetP = C[P1].intersection(C[P2])
                if len(STSetP) >= self.__minOcp:
                    P = tuple(set(P1).union(P2))
                    if not self.__sameLength:
                        UBO = self.__getUBO(STSetP)
                        if UBO >= self.__minOcp:
                            Ck[P] = STSetP
                            ocp = self.__getOcp(P, STSetP)
                            if ocp >= self.__minOcp:
                                self.__HOIs[P] = ocp
                    else:
                        Ck[P] = STSetP
                        ocp = self.__getOcp(P, STSetP)
                        if ocp >= self.__minOcp:
                            self.__HOIs[P] = ocp
            if len(Ck) > 1:
                self.__mineDepth(Ck)
    
    def run(self):
        # scan database to obtain support transaction set of each 1-itemset,
        # length of each transaction, and determine if they have the same length
        STSet = dict()
        with open(self.__srcFile, 'r') as file:
            i = 0
            for line in file:
                trans = line.split()
                self.__lenTrans.append(len(trans))
                if len(trans) != self.__lenTrans[0]:
                    self.__sameLength = False
                for item in trans:
                    item = tuple([item])
                    if item not in STSet:
                        STSet[item] = set()
                    STSet[item].add(i)
                i += 1
            self.__minOcp *= i

        # mine 1-itemsets
        C1 = self.__mine1Itemset(STSet)

        # mine k-itemsets by using depth first search
        if len(C1) > 1:
            self.__mineDepth(C1)
    
    def export(self, desFile):
        with open(desFile, 'w') as file:
            for key, val in self.__HOIs.items():
                text = '{} {:.2f}\n'.format(key, val)
                file.write(text)