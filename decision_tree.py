from heapq import *
import pygame, time, numpy, sys, math




#DECISION TREE CLASS AND FUNCTIONS START
#decision tree node
class Node:
    cls = None #значение класса: 0 - не поливаем, 1 - поливаем, None - не смотрим на эту переменную (узел не конечный)
    l = None #левый дочерний узел
    r = None #правый дочерний узел
    attrinbuteIndex = None #номер атрибута, по которому происходит выбор в данном узле
    attributeNames = [] #список названий атрибутов
    classNames = [] #список названий классов
    attributeConditions = [] #список значений атрибутов (дождь, нет дождя, лук, капуста, ...)
    root = None #ссылка на корневой узел (в корневом узле храним attributeNames, classNames, attributeConditions)
    nodeId = 0
    side = None
    size = 0
    parent = None

    #конструктор, передаем туда ссылку на корневой узел или ничего (None)
    def __init__(self, root, nodeId, side):
        if root != None: #если передали ссылку на корневой узел, то записываем в рут
            self.root = root
        else: #слит не передали
            self.root = self #то в рут записываем ссылку на самого себя
        self.nodeId = nodeId
        self.side = side

    #set symbolic names for attributes and classes
    def assignNames(self, attributeNames, classNames, attributeConditions):
        self.attributeNames = attributeNames
        self.classNames = classNames
        self.attributeConditions = attributeConditions

    #set test instances
    def assignInstances(self, instances):
        self.instances = instances #передаем в текущий узел тестовые наборы, которые ему соответствуют

    #get decision by attribute values
    def getDecision(self, attributes):
        if self.cls is not None: #если в переменной cls что-то есть, то это конечный узел и в cls хранится решение: поливать или нет; возвращаем его
            return self.cls
        if attributes[self.attrinbuteIndex]: #если фактическое значение атрибута с номером attrinbuteIndex равно 1,
            return self.r.getDecision(attributes) #то запрашиваем решение из правого дочернего узла
        else: #а если там 0
            return self.l.getDecision(attributes) #то лезем в левый дочерний узел за решением

    def test(self, instances):
        print('test start')
        for test in trainingInstances:
            decision = self.getDecision(test[:-1:])
            print(decision == test[-1])
        print('end\n')

    #learning - choose better attribute for current node by Information Gain
    def chooseAttribute(self, instances):
        n = len(instances[0]) #в n записываем количество тестовых наборов
        maxGainIndex = 0 #переменная для хранения номера атрибута с максимальным gain
        maxGain = 0 #переменная для хранения максимального gain для данного набора атрибутов
        for i in range(n - 1): #для каждого тестового набора
            g = gain(instances, i) #вычисляем gain для атрибута с номером i
            if (g > maxGain): #если текущий g (gain) больше того, что записано в maxGain, то обновляем maxGain, maxGainIndex
                maxGain = g
                maxGainIndex = i
        self.attrinbuteIndex = maxGainIndex #записываем номер атрибута с максимальным gain в self.attrinbuteIndex
        cl = self.checkLeaf() #проверяем, можно ли считать этот узел конечным (cl > 0)
        if (cl >= 0): #если да
            self.cls = cl #записываем в self.cls значение класса (0 - не поливаем, 1 - поливаем)
        if maxGain == 0: #если maxGain == 0 (то есть аттрибуты не влияют на решение (класс))
            self.cls = self.instances[0][n-1] #то записываем значение класса из нулевого элеменита тестового набора в cls узла
        if self.cls == None: #если cls == None, то есть узел не конечный
            self.constructChilds() #то строим дочерние узлы

    #check if current node is leaf
    def checkLeaf(self): #Если в каждом тестовом наборе один и тот же класс, то этот узел конечный и возвращаем значение класса: 1 или 0
        n = len(self.instances[0])
        prevClass = self.instances[0][n-1]
        for instance in self.instances:
            if instance[n-1] != prevClass:
                return -1 #если нет, то возвращаем -1
        return prevClass


    #divide test instances of current node to child nodes
    def constructChilds(self):
        print('Constructing childs')
        leftInstances = [] #список элементов тестового набора для левого узла
        rightinstances = [] #список элементов тестового набора для правого узла
        for instance in self.instances: #для каждого элемента тестового набора узла
            if not instance[self.attrinbuteIndex]: #если значение атрибута равно 0
                leftInstances.append(instance) #добавляем этот элемент в список для левого узла
            else: #если 1
                rightinstances.append(instance) #то для правого
        if (self.root == None): #если нет ссылки на корневой узел
            self.l = Node(self, 1, 'l') #то создаем дочерний левый узел и передаем туда ссылку на себя
            root.size += 1
        else:
            self.l = Node(self.root, self.root.size + 1, 'l') #иначе создаем левый узел и передаем туда ссылку на корневой узел
            self.root.size += 1
        self.l.parent = self
        self.l.assignInstances(leftInstances) #передаем в созданный левый дочерний узел отобранные для него элементы из тестового набора
        self.l.chooseAttribute(leftInstances) #запускаем выбор атрибута для левого дочернего узла

        #аналогично для правого дочернего узла
        if (self.root == None):
            self.r = Node(self, 2, 'r')
            root.size += 1
        else:
            self.r = Node(self.root, self.root.size + 1, 'r')
            self.root.size += 1
            self.r.parent = self
        self.r.assignInstances(rightinstances)
        self.r.chooseAttribute(rightinstances)

    def save(self, f):
        f.write(str(self.nodeId))
        f.write(' ')
        if self.parent != None:
            f.write(str(self.parent.nodeId))
        else:
            f.write('-1')
        f.write(' ')
        f.write(str(self.side))
        f.write(' ')
        f.write(str(self.attrinbuteIndex))
        f.write(' ')
        f.write(str(self.cls))
        f.write('\n')
        if self.l != None:
            self.l.save(f)
        if self.r != None:
            self.r.save(f)


#calculating Entrophy of test set
def entrophy(instances):
    countLeft = 0 #количество левых примеров (где класс = 1, то есть поливаем)
    countRight = 0 #количество правых примеров в тестовом наборе (то есть количество случаев, когда не поливаем)
    n = 0
    for instance in instances: #в цикле подсчитываем количество правых и левых примеров
        n = len(instance)
        if instance[n - 1]:
            countLeft = countLeft + 1
        else:
            countRight = countRight + 1
    if not countLeft or not countRight: #если есть только правые или только левые примеры, то энтропия равна 0
        return 0
    n = len(instances)
    return -(countLeft / n * math.log2(countLeft / n) + countRight / n * math.log2(countRight / n)) #энтропия по формуле с сайта

#calculation Information Gain of test set for current attribute
def gain(instances, attributeIndex):
    leftInstances = []
    rightInstances = []
    for instance in instances: #в цикле разбиваем примеры на leftInstances и rightInstances в зависимости от значения атрибута с индексом attributeIndex
        if instance[attributeIndex]:
            leftInstances.append(instance)
        else:
            rightInstances.append(instance)
    #вычисляем gain по формуле
    return entrophy(instances) - (len(leftInstances) / len(instances) * entrophy(leftInstances) + len(rightInstances) / len(instances) * entrophy(rightInstances))

#DECISION TREE CLASS AND FUNCTIONS END


#training instances: day of week (0 - odd, 1 - even), is rain (0 - no, 1- yes), kind of vegetable (0 - onion, 1 - carrot), class (0 - not water, 1 - water)
trainingInstances = numpy.array([ #training наборы
    [1, 1, 0, 1, 0, 1, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 0],
    [1, 1, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 1, 0, 1, 0, 1],
    [0, 0, 1, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 1, 1, 1, 1],
    [1, 0, 1, 0, 1, 1, 1, 0]
])

testInstances = numpy.array([ #training наборы
    [1, 0, 1, 0, 1, 1, 1, 0],
    [0, 1, 1, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 0, 0, 1, 0]
])


attributeNames = numpy.array(['Day of week', 'Is Rain', 'Vegetable', 'Ferlilize', 'HowLongAgo', 'NewPlant', 'IsHot'])
classNames = numpy.array(['Skip', 'Water'])
attributeConditions = numpy.array(['odd', 'even',
                                   'No', 'Yes',
                                   'Onion', 'carrot',
                                   'No', 'Yes',
                                   'LongAgo', 'NotLongAgo',
                                   'Old', 'New',
                                   'Hot', 'Cold'])


root = Node(None, 0, None) #создаем корневой узел
root.assignInstances(trainingInstances) #кидаем туда все тестовые данные
root.assignNames(attributeNames, classNames, attributeConditions) #передаем в корневой узел названия для атрибутов, классов и условий
root.chooseAttribute(trainingInstances) #запускаем процесс построения дерева решений
root.test(testInstances)
f = open("dec_tree.txt","w+")
root.save(f)
f.close()
print("end")
