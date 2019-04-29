from heapq import *
import pygame, time, numpy

def heuristic(a, b):
    return (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2

def astar(array, start, goal):

    start = (start[0]-1, start[1])

    neighbors = [(0,1),(0,-1),(1,0),(-1,0)]

    close_set = set()
    came_from = {}
    gscore = {start:0}
    fscore = {start:heuristic(start, goal)}
    oheap = []

    heappush(oheap, (fscore[start], start))

    while oheap:

        current = heappop(oheap)[1]

        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:
                    if array[neighbor[0]][neighbor[1]] == 1:
                        continue
                else:
                    # array bound y walls
                    continue
            else:
                # array bound x walls
                continue

            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue

            if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heappush(oheap, (fscore[neighbor], neighbor))

    return False




map = numpy.array([
    [0,1,1,0,0,0],
    [0,1,1,0,1,0],
    [0,1,1,0,1,0],
    [0,0,0,0,1,0],
    [0,1,0,1,1,0],
    [0,0,0,0,0,0]])

start = (0,0)
finish = (3,5)

steps =  astar(map, start, finish)
steps = steps[::-1]




pygame.init()
road = pygame.image.load("road.png")
field = pygame.image.load("field.png")
tractor = pygame.image.load("tractor.png")
home = pygame.image.load("home.png")

roadrect = road.get_rect()
fieldrect = field.get_rect()
tractorrect = tractor.get_rect()
homerect = home.get_rect()

w, h = roadrect.width, roadrect.height

size = width, height = len(map[0])*w, len(map)*h
screen = pygame.display.set_mode(size)

y = h/2
for line in map:
    x = w/2
    for obj in line:
        if obj == 0:
            roadrect.center = (x, y)
            screen.blit(road, roadrect)
        if obj == 1:
            fieldrect.center = (x, y)
            screen.blit(field, fieldrect)
        x += w
    y += h


homerect.center = ((steps[-1][1])*w + w/2, (steps[-1][0])*h+h/2)
screen.blit(home, homerect)

for step in steps[:-1]:
    tractorrect.center = ((step[1])*w + w/2, (step[0])*h+h/2)
    screen.blit(tractor, tractorrect)

    pygame.display.flip()
    time.sleep(0.3)


while(True):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
