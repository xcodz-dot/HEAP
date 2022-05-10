"""
Neural Networks
===============

A very basic neural network

Genome
------

Format
[1-bit high=FromInput   low=FromNeuron]
[1-bit high=ToOutput    low=ToNeuron]
 [6-bit padding]
[8-bit NeuronIdIn]
[8-bit NeuronIdOut]
[32-bit Weight]
[32-bit Bias]
"""

import copy
import array
import struct
import random
import math

try:
    rng = random.SystemRandom()
except:
    rng = random.Random()
    rng.seed()

GENOME_STRUCT_SIZE = 11

def appropriate_genome_part_random(IC, NC, OC):
    return (((int(rng.randint(0, 5) > 4) << 7) | +
        (int(rng.randint(0, 5) > 4) << 6)).to_bytes(1, 'big') +
        rng.randint(0, max(IC, NC)-1).to_bytes(1, 'big') +
        rng.randint(0, max(OC, NC)-1).to_bytes(1, 'big') +
        struct.pack(">f", rng.uniform(-2.0, 2.0)) +
        struct.pack(">f", rng.uniform(-1.0, 1.0)))

def unpackgenome(block: bytes):
    From = bool(block[0] & 0b1000_0000)
    To = bool(block[0] & 0b0100_0000)
    NeuronIdIn = block[1]
    NeuronIdOut = block[2]
    Weight = struct.unpack(">f", block[3:7])[0]
    Bias = struct.unpack(">f", block[7:11])[0]
    return (From, To, NeuronIdIn, NeuronIdOut, Weight, Bias)


class NN:
    def __init__(self, inputs: int = 0, outputs: int = 0, neurons: int = 2, genome: bytes = b""):
        self.inputs = array.array('f', [0.0 for _ in range(inputs)])
        self.outputs = array.array('f', [0.0 for _ in range(outputs)])
        self.genome = genome
        self.genome_decoded = []
        for x in range(0, len(genome), GENOME_STRUCT_SIZE):
            block = genome[x:x+GENOME_STRUCT_SIZE]
            self.genome_decoded.append(Connection(*unpackgenome(block)))
        self.neurons = array.array('f', [0.0 for _ in range(outputs)])
    
    def simulate(self):
        """
        Simulates precicely one step
        """
        self.neurons_new = [array.array('f') for _ in range(len(self.neurons))]
        self.outputs_new = [array.array('f') for _ in range(len(self.outputs))]
        for x in self.genome_decoded:
            try:
                if x.From:
                    ival = self.inputs[x.NeuronIdIn]
                else:
                    ival = self.neurons[x.NeuronIdIn]
                
                oval = math.tanh(ival*x.Weight + x.Bias)
                
                if x.To:
                    self.outputs_new[x.NeuronIdOut].append(oval)
                else:
                    self.neurons_new[x.NeuronIdOut].append(oval)

                try:
                    for x, v in enumerate(self.neurons_new):
                        self.neurons[x] = sum(v)/len(v)
                except ZeroDivisionError:
                    pass
                try:
                    for x, v in enumerate(self.outputs_new):
                        self.outputs[x] = sum(v)/len(v)
                except ZeroDivisionError:
                    pass
            except IndexError:
                pass

    def reproduce(self, mutation: float):
        if rng.uniform(0.0, 1.0) < mutation:
            genome = self.genome
            for x in range(5):
                rindex = rng.randint(0, len(genome)//GENOME_STRUCT_SIZE)*GENOME_STRUCT_SIZE
                genome = genome.replace(genome[rindex: rindex+GENOME_STRUCT_SIZE], appropriate_genome_part_random(len(self.inputs), len(self.neurons), len(self.outputs)))
        else:
            genome = self.genome
        return NN(len(self.inputs), len(self.outputs), len(self.neurons), genome)

class Connection:
    def __init__(self, From: bool, To: bool, NeuronIdIn: int, NeuronIdOut: int, Weight: float, Bias: float): 
        self.From = From
        self.NeuronIdIn = NeuronIdIn
        self.NeuronIdOut = NeuronIdOut
        self.To = To
        self.Weight = Weight
        self.Bias = Bias
