import pygame
import pickle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("simdata", help="Simulation Data file", default="simdata.pickle", nargs="?")
parser.add_argument("-u", "--uncontrolled", action="store_true", help="If the simulation is to be carried out without inputs")
args = parser.parse_args()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
AIMRECT = (
    (90, 90),
    (101, 101)
)
AIMRECT = pygame.Rect(AIMRECT[0], (AIMRECT[1][0]-AIMRECT[0][0], AIMRECT[1][1]-AIMRECT[0][1]))

pygame.init()
window = pygame.display.set_mode((512, 512))
simdata = pickle.load(open(args.simdata, "rb"))
running = True
clock = pygame.time.Clock()
FPS = 30
print("LOADED")

subsurface = pygame.Surface((101, 101))
simcont = False
current_frame = 0
msgfin = True

while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RIGHT:
                simcont = True
        if ev.type == pygame.KEYUP:
            if ev.key == pygame.K_RIGHT:
                simcont = False
            if ev.key == pygame.K_DOWN:
                running = False
    clock.tick(FPS)
    if simcont or args.uncontrolled:
        subsurface.fill(WHITE)
        
        # Do Stuff
        if current_frame + 1 == len(simdata):
            if msgfin:
                print("FINISHED")
                msgfin = False
            if args.uncontrolled:
                running = False
            continue
        frame = simdata[current_frame]
        current_frame += 1

        pygame.draw.rect(subsurface, (200, 255, 200), AIMRECT)
        pixellock = pygame.PixelArray(subsurface)

        for x in frame:
            pixellock[x[0], x[1]] = BLACK

        del pixellock

        window.blit(pygame.transform.scale(subsurface, (512, 512)), (0, 0))
        pygame.display.update()

pygame.quit()
