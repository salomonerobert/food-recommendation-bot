from locale import currency
import sys
import json

class Heap:

    def __init__(self, arr):
        self.maxsize = sys.maxsize
        self.size = len(arr)
        self.Heap = arr
        self.FRONT = 0

    
    def parent(self, pos):
        return (pos-1)//2 if pos != 0 else 0
    
    def leftChild(self, pos):
        return (2*pos)+1

    def rightChild(self, pos):
        return (2*pos)+2
    
    def isLeaf(self, pos):
        return (2*pos)+1 > self.size

    def swap(self, fpos, spos):
        self.Heap[fpos], self.Heap[spos] = self.Heap[spos], self.Heap[fpos]
    
    def bubbleDown(self, pos, comparer):

        child = self.leftChild(pos)
        done = False

        while child < self.size and not done:
            rightC = self.rightChild(pos)
            if rightC < self.size and comparer(self.Heap[child], self.Heap[rightC]):
                child = rightC

            if comparer(self.Heap[pos], self.Heap[child]):
                self.swap(pos, child)
            else:
                done = True
            
            pos = child
            child = self.leftChild(pos)

    
    def insert(self, item, comparer):
        if self.size >= self.maxsize:
            return
        self.Heap[self.size] = item
        curr = self.size

        self.size += 1

        while comparer(self.Heap[self.parent(curr)],self.Heap[curr]):
            self.swap(curr, self.parent(curr))
            curr = self.parent(curr)
    
    def heapify(self, comparer):

        for pos in range(self.parent(self.size-1), -1, -1):
            self.bubbleDown(pos, comparer)
    
    def remove(self, comparer):
        popped = self.Heap[self.FRONT]
        self.Heap[self.FRONT]= self.Heap[self.size-1]
        self.size -= 1
        self.bubbleDown(self.FRONT, comparer)
        return popped

    def Print(self):
        for i in range(0, self.parent(self.size-1), 1):
            print(" PARENT : "+ str(self.Heap[i])+" LEFT CHILD : "+ 
                                str(self.Heap[2 * i])+" RIGHT CHILD : "+
                                str(self.Heap[2 * i + 1]))

class getItemsByField:

    """
    Class to heapify array and retrieve top items. Takes in list of dictionaries, field for sorting and boolean value for ascending/descending order of sort.
    """

    def __init__(self, arr, field, isAscending=True):
        self.arr = arr
        self.field = field
        self.isAscending = isAscending
        self.newHeap = Heap(arr)
        self.removedItems = []
        self.getNextCounter = 0
        self.getPrevCounter = 0
        self.pageNo = 0
        self.maxPages = len(self.arr)//5 + (0 if len(self.arr)%5 == 0 else 1)

    def getNextN(self, nextN):
        """
        Returns top N items in a list of dictionaries
        """

        def ascendingComparer(a,b):
             return a[self.field]+(1/a['distance'])>b[self.field]+(1/b['distance'])

        def descendingComparer(a,b):
            return a[self.field]+(1/a['distance'])<b[self.field]+(1/b['distance'])

        if len(self.removedItems) == 0:
            self.newHeap.heapify(ascendingComparer if self.isAscending == True else descendingComparer)
        
        self.pageNo = self.getNextCounter - self.getPrevCounter
        sortedList = []

        if self.pageNo+1 > self.maxPages:
            self.getNextCounter = self.getPrevCounter + self.maxPages + 1 #set page to max+1
            self.pageNo = self.getNextCounter - self.getPrevCounter
            return []
        elif (self.pageNo+1)*5 > len(self.removedItems) and (len(self.removedItems)//5 + (0 if len(self.removedItems)%5==0 else 1)) < self.pageNo+1: #extracting new items from Heap
            self.getNextCounter += 1
            self.pageNo = self.getNextCounter - self.getPrevCounter
            nextN = min(nextN,len(self.arr)-len(self.removedItems))
            for j in range(nextN):
                sortedList.append(self.newHeap.remove(ascendingComparer if self.isAscending == True else descendingComparer))
        else:
            self.getNextCounter += 1
            self.pageNo = self.getNextCounter - self.getPrevCounter
            return(self.removedItems[(self.pageNo-1)*5 : min(self.pageNo*5,len(self.removedItems))])

        self.removedItems += sortedList


        return sortedList

    def getPrevN(self, prevN):
        """
        Function returns previous N elements that have been extracted from the heap in sorted order.
        Function is designed to work with non-consistent values of N.
        """
        self.pageNo = self.getNextCounter - self.getPrevCounter

        if self.pageNo <= 1:
            self.getPrevCounter = self.getNextCounter #set page number to 0
            self.pageNo = self.getNextCounter - self.getPrevCounter
            return []
        else: 
            self.getPrevCounter += 1
            self.pageNo = self.getNextCounter - self.getPrevCounter
            return self.removedItems[(self.pageNo-1)*prevN : min(self.pageNo*prevN,len(self.removedItems))]

        
    
def example():
    dir="yelpAPIData.json"
    f=open(dir,encoding='utf-8')
    data=json.load(f)

    temp = getItemsByField(data, 'distance', True)

    for i in range(5):
        output = temp.getNextN(5)

        print(i)
        for j in range(len(output)):
            print(output[j]['name'], output[j]['distance'])

    output2 = temp.getPrevN(5)
    for k in range(len(output2)):
            print(output2[k]['name'], output2[k]['distance'])

    output2 = temp.getPrevN(5)
    for k in range(len(output2)):
            print(output2[k]['name'], output2[k]['distance'])

    output2 = temp.getNextN(5)
    for k in range(len(output2)):
            print(output2[k]['name'], output2[k]['distance'])


