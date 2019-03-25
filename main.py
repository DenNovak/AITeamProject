import pygame



pygame.init()
win = pygame.display.set_mode((500, 500))

pygame.display.set_caption("Field")



width = 40
height = 60
vel = 5

image = pygame.image.load("tractor.resized.png")
def trac(x, y):
    win.blit(image, (x, y))

x = 0
y = 0

run = True
while(run):
    pygame.time.delay(100) #like a clock

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and x > vel:
        x -= vel
        x += vel
    if keys[pygame.K_RIGHT] and x < (500 - width - vel):                        #moving character
        x += vel
    if keys[pygame.K_UP] and y > 0:
        y -= vel
    if keys[pygame.K_DOWN] and y < (500 - height - vel):
        y += vel

    win.fill(1)
    trac(x, y)

    if(x != (500 - width)):
        x += 20
    if(x == (500 - width)):
        y+=20
        x = 0


    # win.fill(1)
    # trac(x,y)


    pygame.display.update()

pygame.quit()
