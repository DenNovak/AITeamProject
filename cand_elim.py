from heapq import *
import pygame, time, numpy, sys, math


#CANDIDATE ELIMINATION FUNCTIONS START
#Функция, в которой обучаем машину
def learn(samples):
    G = [] #генеральное множество гипотез (то есть правил, по которым принимается решение)
    S = [] #специфическое множество гипотез - гипотезы, соответстыующие тестовым данным (это множество в общем-то не нужно, но в статье было)
    g0 = [] #начальный элемент множества G
    s0 = [] #начальный элемент множества S
    fv = getFeatureValues(samples) #заполняем в переменную fv все возможные значения (features) из тестовых данных
    for i in range(len(samples[0]) - 1):
        g0.append('?') #заполняем начальное значение g0 знаками вопроса, то есть изначально считаем, что каждая feature может иметь любое значение
        s0.append('0') #начальное значение s0 заполняем нулями, что означает, что ни один из тестовых примеров не соответсвует истине
    G.append(g0) #добавляем начальную гипотезу в G
    S.append(s0) #добавляем начальную гипотезу в S
    print('G: ', G)
    print('S: ', S)

    #для каждого тестового примера
    for i in range(len(samples)):
        e = samples[i] #пример
        n = len(e) #длина примера
        if e[n - 1] == '1': #если это позитивный пример
            G = removeNegative(G, e) #удаляем из G гипотезы, которые не соответствуют примеру
            S = minGeneralize(S, e) #удаляем из S гипотезы, которые не соответствуют примеру, а вместо них вписываем наиболее специфичную генерализацию
            S = removeNonMaximal(S) #удаляем из S гипотезы, которые являются генерализацией какой-либо другой гипотезы из S
        else: #если это негативный пример
            S = removePositive(S, e) #удаляем из S гипотезы, соответствующие примеру
            G = minSpecialize(G, e, fv) #удаляем из G гипотезы, соответствующие примеру, а вместо них вписываем наиболее общие специализации
            G = removeNonMinimal(G) #удаляем из G гипотезы, для которых есть более общие гипотезы в G
        print('G: ', G)
        print('S: ', S)
    return G, S

#функция выбирает из тестового набора значения features (например: трава, земля, кукуруза, подсолнечник, ...)
def getFeatureValues(samples):
    fv = [[], []]
    n = len(samples[0])
    for j in range(n - 1):
        fv[0].append(0)
        fv[1].append(0)
    for e in samples:
        for i in range(n - 1):
            if fv[0][i] == 0:
                fv[0][i] = e[i]
            else:
                if fv[0][i] != e[i]:
                    fv[1][i] = e[i]
    return fv

#функция возвращает противоположное значение заданной фичи (feature) с индексом index и значением val (например, для подсолнуха вернет кукурузу как противоположный вариант)
def getAnotherValue(fv, index, val):
    if fv[0][index] != val:
        return fv[0][index]
    else:
        return fv[1][index]
            
#удаляет из S гипотезы, соответствующие примеру e
def removePositive(S, e):
    print('remove positive')
    toRemove = []
    for s in S:
        if testPositive(s, e):
            toRemove.append(s)
    for item in toRemove:
        S.remove(item)
        print('removing ', item, ' from S')
    return S

#удаляет из G гипотезы, не соответствующие примеру е
def removeNegative(G, e):
    print('removing negative')
    toRemove = []
    for g in G:
        if not testPositive(g, e):
            toRemove.append(g)
    for item in toRemove:
        G.remove(item)
    return G

#заменяет в S гипотезы, не соответствующие примеру e на соответствующие, полученные в результате минимальной генерализации
def minGeneralize(S, e):
    for s in S:
        if not testPositive(s, e):
            for i in range(len(e) - 1):
                if not testFeature(s[i], e[i]):
                    if s[i] == '0':
                        s[i] = e[i]
                    else:
                        s[i] = '?'
    return S

#заменяет в G гипотезы, соответствующие примеру e на несоответствующие, полученные в результате минимальной специализации
def minSpecialize(G, e, fv):
    toRemove = []
    toAdd = []
    for g in G: #для каждой гипотезы в G
        if testPositive(g, e): #если пример соответствует гипотезе
            for i in range(len(e) - 1): #для каждой фичи
                if (g[i]) == '?': #если гипотеза допускает любое значение фичи
                    newG = []
                    #добавляем гипотезу, у которой эта фича противоположная
                    for j in range (len(e) - 1):
                        if i == j:
                            newG.append(getAnotherValue(fv, j, e[j]))
                        else:
                            newG.append(g[j])
                    toAdd.append(newG)
            toRemove.append(g) #старую гипотезу удаляем
    for item in toRemove:
        G.remove(item)
    for item in toAdd:
        G.append(item)
    return G

#Удаляем из S гипотезы, являющиеся генерализацией какой-либо другой гипотезы из S
def removeNonMaximal(S):
    print('removing non maximal')
    toRemove = []
    n = len(S)
    for i in range(n):
        for j in range(n):
            if i != j and isMoreGeneral(S[j], S[i]):
                if not S[j] in toRemove:
                    toRemove.append(S[j])
    for item in toRemove:
        S.remove(item)
    return S

#Удаляем из G гипотезы, являющиеся специализацией какой-либо другой гипотезы из G
def removeNonMinimal(G):
    print('removing non minimal')
    toRemove = []
    n = len(G)
    for i in range(n):
        for j in range(n):
            if i != j and isMoreSpecific(G[j], G[i]):
                if not G[j] in toRemove:
                    toRemove.append(G[j])
    for item in toRemove:
        G.remove(item)
    return G

#проверка примера е на соответствие гипотезе h
def testPositive(h, e):
    for i in range(len(h)):
        if not testFeature(h[i], e[i]):
            return 0
    return 1

#проверка соответствия фактического и гипотетического значения фичи
def testFeature(hf, f):
    if hf == '0' or hf != f and hf != '?':
        return 0
    return 1

#true если гипотеза h1 является генерализацией (обобщением) гипотезы h2
def isMoreGeneral(h1, h2):
    return compare(h1, h2) > 0 and testPositive(h1, h2)

#true если гипотеза h1 является специализацией гипотезы h2
def isMoreSpecific(h1, h2):
    return compare(h1, h2) < 0 and testPositive(h2, h1)

#функция возвращает положительное значение, если первая гипотеза является обобщением второй, 0, если равнозначны, отрицательное, если первая гипотеза является специализацией (частным случаем) другой
def compare(h1, h2):
    n = len(h1)
    s1 = 0
    s2 = 0
    for i in range(n):
        if h1[i] != '0' and h1[i] != '?':
            s1 = s1 + 1;
        if h1[i] == '?':
            s1 = s1 + 2
        if h2[i] != '0' and h2[i] != '?':
            s2 = s2 + 1;
        if h2[i] == '?':
            s2 = s2 + 2
    return s1 - s2
        
#главная функция, которая выдает 1 если пример e соответствует гипотезам и 0, если не соответствует
#например, для примера 'незасеянная земля', 'есть семена кукурузы', 'почва песчаная' выдаст 1, то есть сеять
# а для примера 'засеянная земля', 'есть семена кукурузы', 'почва песчаная' выдаст 0, то есть не сеять
def getDecision(G, e):
    for g in G:
        if testPositive(g, e):
            return 1
    return 0

#CANDIDATE ELIMINATION FUNCTIONS END

#примеры для обучения
train = numpy.array([['grass', 'onion', 'sand', 0],
                     ['soil', 'onion', 'clay', 0],
                     ['soil', 'onion', 'sand', 1],
                     ['grass', 'carrot', 'sand', 0],
                     ['soil', 'carrot', 'sand', 1]])
    #запускаем обучение
G, S = learn(train)

test = numpy.array([['grass', 'carrot', 'sand', 0],
                     ['grass', 'onion', 'clay', 0],
                     ['soil', 'carrot', 'sand', 1]])

for inst in test:
    if getDecision(G, inst) == int(inst[len(inst) - 1]):
        print('PASS')
    else:
        print('FAIL')

f = open("cand_elim.txt","w+")
for g in G:
    for s in g:
        f.write(s)
        f.write(" ")
    f.write("\n")
    
f.close()
