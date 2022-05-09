import pickle
import random
import nn
import argparse
import struct
import math

"""
Inputs
======

0 = Distance West
1 = Distance East
2 = Distance North
3 = Distance South
4 = Distance from safezone

Outputs
=======
 
0 = Move Left
1 = Move Right
2 = Move Up
3 = Move Down
"""

IC = 5
OC = 4
NC = 4
ccount = 50
SIMCOUNT = 120
GSIZE = 24
psize = 100
MUTATION_RATE = 0.05
AIMRECT = (
    (90, 90),
    (101, 101)
)

def inrect(c, rect):
    return (c.x in range(rect[0][0], rect[1][0])) and (c.y in range(rect[0][1], rect[1][1]))

def appropriate_genome_part_random():
    return struct.pack(
        nn.GENOME_STRUCT,
        random.randint(0, 5) > 4,
        random.randint(0, 5) > 4,
        random.randint(0, max(IC, NC)-1),
        random.randint(0, max(OC, NC)-1),
        random.uniform(-1.0, 1.0),
        random.uniform(-1.0, 1.0)
    )

def appropriate_genome_random():
    d = b''
    for x in range(GSIZE):
        d += appropriate_genome_part_random()
    return d

class Creature:
    def __init__(self, nn):
        self.x = random.randint(0, psize)
        self.y = random.randint(0, psize)
        while inrect(self, AIMRECT):
            self.x = random.randint(0, psize)
            self.y = random.randint(0, psize)
        self.nn = nn
    
    def simulate(self):
        self.nn.inputs[0] = self.x / psize
        self.nn.inputs[1] = (psize - self.x) / psize
        self.nn.inputs[2] = self.y / psize
        self.nn.inputs[3] = (psize - self.y) / psize
        self.nn.inputs[4] = math.dist(((AIMRECT[0][0]+AIMRECT[1][0])/2, (AIMRECT[0][1]+AIMRECT[1][1])/2), (self.x, self.y)) / psize
        self.nn.simulate()

        # print(self.nn.outputs)

        if self.nn.outputs[0] > 0 and self.x > 0:
            self.x -= 1
        if self.nn.outputs[1] > 0 and self.x < psize:
            self.x += 1
        if self.nn.outputs[2] > 0 and self.y > 0:
            self.y -= 1
        if self.nn.outputs[3] > 0 and self.y < psize:
            self.y += 1

parser = argparse.ArgumentParser()
parser.add_argument("file", help="File Name", default=None, nargs='?')
parser.add_argument("-o", "--output", help="File to write SIMDATA to", default="simdata.pickle")
parser.add_argument("-n", "--output-nextgen", help="File to write Next Generation beings", default="selected.pickle")
args = parser.parse_args()

if args.file:
    print("Loading from file")
    file = open(args.file, 'rb')
    data = pickle.load(file)
    creatures = []
    for x in data:
        creatures.append(Creature(nn.NN(IC, OC, NC, x)))
else:
    print("Generating Creatures")
    creatures = []
    for x in range(ccount):
        creatures.append(Creature(nn.NN(IC, OC, NC, appropriate_genome_random())))
        print(f'\r{int((x+1/(ccount))*100)}%', flush=True, end="")


# At this point, we are done with generation of either first creatures
# Or reproducing from previously selected creatures.
# Now we will simulate them for as long as needed

simdata = []

for x in range(SIMCOUNT):
    sdata = []
    print(f"\rSimulating: {int((x+1/(SIMCOUNT))*100)}%", flush=True, end="")
    for c in creatures:
        c.simulate()
        sdata.append([c.x, c.y, c.nn.genome])
    simdata.append(sdata)

nextnn = []
jdo = False
if not any([inrect(x, AIMRECT) for x in creatures]):
    creatures.clear()
    for x in range(math.ceil(ccount/10)):
        creatures.append(Creature(nn.NN(IC, OC, NC, appropriate_genome_random())))
    jdo = True

while True:
    for c in creatures:
        if inrect(c, AIMRECT) or jdo:
            nextnn.append(c.nn.reproduce(MUTATION_RATE).genome)
            if len(nextnn) == ccount:
                break
    if len(nextnn) == ccount:
            break

pickle.dump(simdata, open(args.output, 'wb'))
pickle.dump(nextnn, open(args.output_nextgen, 'wb'))
