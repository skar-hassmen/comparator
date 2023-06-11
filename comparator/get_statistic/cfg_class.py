from collections import defaultdict


class CfgNode:
    def __init__(self, nodenum, address, label=None, defList=[], useList=[]):
        self.nodenum = str(nodenum)
        self.address = address
        if label:
            self.label = label
        else:
            self.label = address
        self.defList = defList
        self.useList = useList
        self.ddList = set()
        self.xrefsFromNode = []
        self.xrefsToNode = []
        self.symbolDefHistory = defaultdict(str)
        self.shadowStack = []

    def __str__(self):
        output_dd_list = ','.join(entry for entry in self.ddList)
        output_str = '\t' + self.nodenum + ' [label=\"' + str(self.label) + '; DD:' + output_dd_list + '\"]\n'
        return output_str


class CfgEdge:
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def __eq__(self, other):
        if isinstance(other, CfgEdge):
            return self.head == other.head and self.tail == other.tail

    def __str__(self):
        output_str = str(self.head) + '->' + str(self.tail)
        return output_str
    