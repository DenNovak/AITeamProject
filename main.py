from heapq import *
import pygame, time, numpy, sys, math, random
from keras.models import model_from_json
import cv2

carrots = numpy.array(["carrot.png", "8.png", "11.png"])
onions = numpy.array(["cybula.png", "3.png", "4.png"])
vegNames = numpy.array([
    ["empty12345678","empty12345678","empty12345678","empty12345678","empty12345678","empty12345678"],
    ["empty12345678","empty12345678","empty12345678","empty12345678","empty12345678","empty12345678"],
    ["empty12345678","empty12345678","empty12345678","empty12345678","empty12345678","empty12345678"],
    ["empty12345678","empty12345678","empty12345678","empty12345678","empty12345678","empty12345678"],
    ["empty12345678","empty12345678","empty12345678","empty12345678","empty12345678","empty12345678"],
    ["empty12345678","empty12345678","empty12345678","empty12345678","empty12345678","empty12345678"]])

carImages = []
for fname in carrots:
    img = pygame.image.load(fname)
    carImages.append(img)
onImages = []
for fname in onions:
    img = pygame.image.load(fname)
    onImages.append(img)

#CAND_ELIM
#карта засеянности: soil - незасеянная земля, grass - засеянная земля
mapSoil = numpy.array([
    ['soil','grass','grass','grass','grass','grass'],
    ['soil','grass','grass','grass','grass','soil'],
    ['soil','grass','grass','grass','grass','soil'],
    ['soil','soil','soil','soil','soil','soil'],
    ['soil','soil','soil','soil','soil','soil'],
    ['soil','soil','soil','soil','soil','soil']])

#карта почвы: песок или глина
soilType = numpy.array([
    ['sand','clay','clay','clay','clay','clay'],
    ['sand','clay','clay','clay','sand','sand'],
    ['sand','clay','sand','clay','clay','sand'],
    ['sand','clay','clay','sand','sand','sand'],
    ['sand','clay','sand','sand','clay','sand'],
    ['sand','sand','sand','clay','sand','sand']])



#DEC_TREE
#field map: 0 - onion 1 - carrot
mapVegatable = numpy.array([ #карта поля c луком и капустой
    [0,1,1,1,1,1],
    [0,1,1,1,1,0],
    [0,1,1,1,1,0],
    [0,0,0,0,0,0],
    [0,0,0,0,0,0],
    [0,0,0,0,0,0]])

#test instances: day of week (0 - odd, 1 - even), is rain (0 - no, 1- yes), kind of vegetable (0 - onion, 1 - carrot), class (0 - not water, 1 - water)
trainingInstances = numpy.array([ #тестовые наборы
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




#ELIMINATION
mapVeg = numpy.array([
    ['onion','carrot','carrot','carrot','carrot','carrot'],
    ['onion','carrot','carrot','carrot','carrot','onion'],
    ['onion','carrot','carrot','carrot','carrot','onion'],
    ['onion','onion','onion','onion','onion','onion'],
    ['onion','onion','onion','onion','onion','onion'],
    ['onion','onion','onion','onion','onion','onion']])

mapDry = numpy.array([
    ['dry','rain','rain','rain','rain','rain'],
    ['dry','rain','rain','rain','dry','dry'],
    ['dry','rain','dry','rain','rain','dry'],
    ['dry','rain','rain','dry','dry','dry'],
    ['dry','rain','dry','dry','rain','dry'],
    ['dry','dry','dry','rain','dry','dry']])

mapFerl = numpy.array([
    ['yes','no','no','no','no','no'],
    ['yes','no','no','no','yes','yes'],
    ['yes','no','yes','no','no','yes'],
    ['yes','no','no','yes','yes','yes'],
    ['yes','no','yes','yes','no','yes'],
    ['yes','yes','yes','no','yes','yes']])



attributeNames = numpy.array(['Day of week', 'Is Rain', 'Vegetable', 'Ferlilize', 'HowLongAgo', 'NewPlant', 'IsHot'])
classNames = numpy.array(['Skip', 'Water'])
attributeConditions = numpy.array(['odd', 'even',
                                   'No', 'Yes',
                                   'Onion', 'carrot',
                                   'No', 'Yes',
                                   'LongAgo', 'NotLongAgo',
                                   'Old', 'New',
                                   'Hot', 'Cold'])

#инициализируем модуль pygame
pygame.init()

#загружаем картинки
tractor = pygame.image.load("tractor.png")
carrot = pygame.image.load("carrot.png")
carrotW = pygame.image.load("carrot_w.png")
cybula = pygame.image.load("cybula.png")
cybulaW = pygame.image.load("cybula_w.png")
clay = pygame.image.load("clay.png")
sand = pygame.image.load("sand.png")
grass = pygame.image.load("grass.png")
nawoz = pygame.image.load("nawoz.png")

#создаем переменные в которых кранятся координаты квадратов для картинок
tractorrect = tractor.get_rect()
carrotrect = carrot.get_rect()
carrotWrect = carrotW.get_rect()
cybularect = cybula.get_rect()
cybulaWrect = cybulaW.get_rect()
clayrect = clay.get_rect()
sandrect = sand.get_rect()
grassrect = grass.get_rect()
nawozrect = nawoz.get_rect()

w, h = carrotrect.width, carrotrect.height #вычисляем ширину и высоту картинки

size = width, height = len(mapVegatable[0])*w, len(mapVegatable)*h #вычисляем размер поля
screen = pygame.display.set_mode(size) #устанавливаем размер окна/поверхности для рисования

#рисуем поле в соответствии с картой
def fillFieldForSeed():
    j = 0
    y = h/2
    for line in mapSoil:
        x = w/2
        i = 0
        for obj in line:
            if obj == 'grass':
                grassrect.center = (x, y)
                screen.blit(grass, grassrect) #тут трава (засеянная земля)
            if obj == 'soil':
                if soilType[j][i] == 'sand':
                    sandrect.center = (x, y)
                    screen.blit(sand, sandrect) #тут песок
                else:
                    clayrect.center = (x, y)
                    screen.blit(clay, clayrect) # тут глина
            x += w
            i += 1
        y += h
        j += 1

#в цикле зполняем поле неполитым луком и капустой
def fillFieldForWater():
    j = 0
    y = h/2
    for line in mapVegatable:
        i = 0
        x = w/2
        for obj in line:
            if obj == 0: #если текущий элемент массива nmapVegatable равен 0, то рисуем луковицу
                cybularect.center = (x, y)
                r = random.randrange(2)
                screen.blit(onImages[r], cybularect)
                vegNames[j][i] = onions[r]
            if obj == 1: #если 1, то капусту
                carrotrect.center = (x, y)
                r = random.randrange(2)
                screen.blit(carImages[r], carrotrect)
                vegNames[j][i] = carrots[r]
            x += w
            i += 1
        y += h
        j += 1
    print(vegNames)


def fillFieldForNawoz():
    j = 0
    y = h/2
    for line in mapVeg:
        x = w/2
        i = 0
        for obj in line:
            if obj == 'onion':
                if mapDry[j][i] == 'dry':
                    cybularect.center = (x, y)
                    screen.blit(cybula, cybularect) #тут песок
                else:
                    cybulaWrect.center = (x, y)
                    screen.blit(cybulaW, cybulaWrect) #тут песок
            if obj == 'carrot':
                if mapDry[j][i] == 'dry':
                    carrotrect.center = (x, y)
                    screen.blit(carrot, carrotrect) #тут песок
                else:
                    carrotWrect.center = (x, y)
                    screen.blit(carrotW, carrotWrect) #тут песок
            x += w
            i += 1
        y += h
        j += 1



#CANDIDATE ELIMINATION
#проверка соответствия фактического и гипотетического значения фичи
def testFeature(hf, f):
    if hf == '0' or hf != f and hf != '?':
        return 0
    return 1

#проверка примера е на соответствие гипотезе h
def testPositive(h, e):
    for i in range(len(h)):
        if not testFeature(h[i], e[i]):
            return 0
    return 1

def getDecision(G, e):
    for g in G:
        if testPositive(g, e):
            return 1
    return 0

def loadHypotises(filename):
    G = []
    f = open(filename,"r")
    for s in f:
        g = []
        print(s)
        args = s.rsplit(' ')
        for a in args:
            if a != '\n':
                g.append(a)
        G.append(g)
    f.close
    return G

#END CANDIDATE ELIMINATIOn


class DecTree:
    l = None
    r = None
    atr = None
    cls = None

    def __init__(self, l, r, atr, cls):
        self.l = l
        self.r = r
        self.atr = atr
        self.cls = cls

    def getDecision(self, attributes):
        if self.cls is not None: #если в переменной cls что-то есть, то это конечный узел и в cls хранится решение: поливать или нет; возвращаем его
            return self.cls
        if attributes[self.atr]: #если фактическое значение атрибута с номером attrinbuteIndex равно 1,
            return self.r.getDecision(attributes) #то запрашиваем решение из правого дочернего узла
        else: #а если там 0
            return self.l.getDecision(attributes)

def loadDecisionTree():
    nodes = []
    f = open("dec_tree.txt","r")
    for s in f:
        print(s)
        args = s.rsplit(' ')
        cls = None
        if (args[4] != 'None\n'):
            cls = int(args[4])
        node = DecTree(None, None, int(args[3]), cls)
        nodes.append(node)
        if args[2] != 'None':
            if args[2] == 'l':
                nodes[int(args[1])].l = node
            else:
                nodes[int(args[1])].r = node
    f.close
    return nodes[0]


def loadNeuralModel():
    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights("model.h5")
    loaded_model.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])
    return loaded_model

def predict(oldI, oldJ, model):
    vegType = mapVegatable[oldJ][oldI]
    print(vegNames[oldJ][oldI])
    img = cv2.imread(vegNames[oldJ][oldI])
    img = img.reshape(1, 50, 50, 3)
    return model.predict(img)

def drawCellSeed(oldI, oldJ, sample, G, attributes):
    if (oldJ > -1):
        sample[0] = mapSoil[oldJ][oldI] #смотрим, растет ли тут что-то
        sample[2] = soilType[oldJ][oldI] #смотрим, какой тип почвы в данной клетке
        decision = getDecision(G, sample) #принимаем решение, сеять семена тут или нет
        if decision: #если сеем, то рисуем либо кукурузу либо подсолнух
            if sample[1] == 'onion':
                cybularect.center = (oldI*w + w/2, oldJ*h+h/2)
                screen.blit(cybula, cybularect)
            else:
                carrotrect.center = (oldI*w + w/2, oldJ*h+h/2)
                screen.blit(carrot, carrotrect)
        else: #если не сеем, то зарисовываем старую позицию трактора травой, песком или глиной
            if mapSoil[oldJ][oldI] == 'grass':
                grassrect.center = (oldI*w + w/2, oldJ*h+h/2)
                screen.blit(grass, grassrect)
            else:
                if soilType[oldJ][oldI] == 'sand':
                    sandrect.center = (oldI*w + w/2, oldJ*h+h/2)
                    screen.blit(sand, sandrect)
                else:
                    clayrect.center = (oldI*w + w/2, oldJ*h+h/2)
                    screen.blit(clay, clayrect)

def drawCellNawoz(oldI, oldJ, sample, G, attributes):
    if (oldJ > -1):
        sample[0] = mapVeg[oldJ][oldI] 
        sample[1] = mapDry[oldJ][oldI]
        sample[2] = mapFerl[oldJ][oldI]
        decision = getDecision(G, sample) 
        if decision: #
            nawozrect.center = (oldI*w + w/2, oldJ*h+h/2)
            screen.blit(nawoz, nawozrect)
        else: #
            if mapVeg[oldJ][oldI] == 'onion':
                cybularect.center = (oldI*w + w/2, oldJ*h+h/2)
                screen.blit(cybula, cybularect)
            else:
                carrotrect.center = (oldI*w + w/2, oldJ*h+h/2)
                screen.blit(carrot, carrotrect)

def drawCellWater(oldI, oldJ, sample, G, attributes, model):
    if (oldJ > -1): #если существуют предыдущее координаты трактора, то зарисовываем предыдущую клетку
        attributes[2] = predict(oldI, oldJ, model) #смотрим, что за растение растет в этой клетке
        decision = root.getDecision(attributes) #спрашиваем у дерева решений, поливать тут или не поливать
        if decision: #если поливать
            if mapVegatable[oldJ, oldI]: #если тут растет капуста, рисуем политую капусту
                carrotWrect.center = (oldI*w + w/2, oldJ*h+h/2)
                screen.blit(carrotW, carrotWrect)
            else: #рисуем политый лук
                cybulaWrect.center = (oldI*w + w/2, oldJ*h+h/2)
                screen.blit(cybulaW, cybulaWrect)
        else: #если не поливать
            if mapVegatable[oldJ, oldI]: #если тут растет капуста, рисуем неполитую капусту
                carrotrect.center = (oldI*w + w/2, oldJ*h+h/2)
                screen.blit(carrot, carrotrect)
            else: #рисуем неполитый лук
                cybularect.center = (oldI*w + w/2, oldJ*h+h/2)
                screen.blit(cybula, cybularect)

def drawWork(workType, G, sample, root, attributes, model):
    oldI = 0
    oldJ = -1
    #в цикле рисуем трактор и растительность
    for i in range(len(mapVegatable)):
        for j in range(len(mapVegatable[i])):
            tractorrect.center = (i*w + w/2, j*h+h/2)
            screen.blit(tractor, tractorrect)
            if workType == 'seed':
                drawCellSeed(oldI, oldJ, sample, G, attributes)
            elif workType == 'water':
                drawCellWater(oldI, oldJ, sample, G, attributes, model)
            elif workType == 'nawoz':
                drawCellNawoz(oldI, oldJ, sample, G, attributes)
                   
            pygame.display.flip()
            oldJ = j
            oldI = i
            time.sleep(0.3)
    if workType == 'seed':
        drawCellSeed(oldI, oldJ, sample, G, attributes)
    elif workType == 'water':
        drawCellWater(oldI, oldJ, sample, G, attributes, model)
    elif workType == 'nawoz':
        drawCellNawoz(oldI, oldJ, sample, G, attributes)
    pygame.display.flip()



G = loadHypotises("cand_elim.txt")
#массив для передачи параметров каждой клетки в функцию получения решения (щас тут прописано, что сеем подсолнух, можно поменять на onion)
sample = [0, 'carrot', 0]
fillFieldForSeed()
drawWork('seed', G, sample, None, None, None)

time.sleep(1.0)

model = loadNeuralModel()

root = loadDecisionTree()
    #устанавливаем погоду и день недели
    # 'Day of week', 'Is Rain', 'Vegetable', 'Ferlilize', 'HowLongAgo', 'NewPlant', 'IsHot'
rain = 0
dayOddEven = 1
attributes = numpy.array([0,0,0,0,0,0,0]) #переменная для хранения дня недели, погоды и вида растения, ее будем передавать в дерево решений
attributes[0] = dayOddEven
attributes[1] = rain
attributes[3] = 1
attributes[4] = 0
attributes[5] = 1
attributes[6] = 0
fillFieldForWater()
drawWork('water', None, None, root, attributes, model)

time.sleep(3.0)

G = loadHypotises("output.txt")
sample = [0, 0, 0]
fillFieldForNawoz()
drawWork('nawoz', G, sample, None, None, None)

#бесконечный цикл в ожидании выхода
while(True):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()