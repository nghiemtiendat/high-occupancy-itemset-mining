class ATHOI:

    def __init__(self, srcFile, numHOIs):
        # path to source file
        self.__srcFile = srcFile
        # number of high occupancy itemsets
        self.__numHOIs = numHOIs
        # minimum occupancy threshold
        self.__minOcp = 0
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
            if len(STSetP) > self.__minOcp:
                ocp = self.__getOcp(P, STSetP)
                if ocp > self.__minOcp:
                    # if number of high occupancy itemsets is not enough
                    # insert new itemset into HOIs
                    if len(self.__HOIs) < self.__numHOIs:
                        self.__HOIs[P] = ocp
                    # otherwise
                    else:
                        # find itemset with smallest occupancy value and remove
                        key = min(self.__HOIs, key=self.__HOIs.get)
                        del self.__HOIs[key]
                        # insert new itemset into HOIs
                        self.__HOIs[P] = ocp
                        # recalculate mininum occupancy threshold
                        self.__minOcp = min(self.__HOIs.values())
                UBO = self.__getUBO(STSetP)
                if UBO > self.__minOcp:
                    C1[P] = STSetP
        return C1
    
    def __mineDepth(self, C):
        itemsets = list(C.keys())
        for i in range(len(itemsets)):
            Ck = dict()
            P1 = itemsets[i]
            for j in range(i+1, len(itemsets)):
                P2 = itemsets[j]
                STSetP = C[P1].intersection(C[P2])
                if len(STSetP) > self.__minOcp:
                    P = tuple(set(P1).union(P2))
                    ocp = self.__getOcp(P, STSetP)
                    if ocp > self.__minOcp:
                        # if number of high occupancy itemsets is not enough
                        # insert new itemset into HOIs
                        if len(self.__HOIs) < self.__numHOIs:
                            self.__HOIs[P] = ocp
                        # otherwise
                        else:
                            # find itemset with smallest occupancy value and remove
                            key = min(self.__HOIs, key=self.__HOIs.get)
                            del self.__HOIs[key]
                            # insert new itemset into HOIs
                            self.__HOIs[P] = ocp
                            # recalculate minimum occupancy threshold
                            self.__minOcp = min(self.__HOIs.values())
                    UBO = self.__getUBO(STSetP)
                    if UBO > self.__minOcp:
                        Ck[P] = STSetP
            if len(Ck) > 1:
                self.__mineDepth(Ck)
    
    def run(self):
        # scan database to obtain support transaction set of each 1-itemset
        # and length of each transaction
        STSet = dict()
        with open(self.__srcFile, 'r') as file:
            i = 0
            for line in file:
                trans = line.split()
                self.__lenTrans.append(len(trans))
                for item in trans:
                    item = tuple([item])
                    if item not in STSet:
                        STSet[item] = set()
                    STSet[item].add(i)
                i += 1
        
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