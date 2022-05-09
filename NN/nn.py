"""
Neural Networks
===============

A very basic neural network

Genome
------

Format
[1-bit high=FromInput   low=FromNeuron]
[1-bit high=ToOutput    low=ToNeuron]
[8-bit NeuronIdIn]
[8-bit NeuronIdOut]
[32-bit Weight]
[32-bit Bias]
"""

import copy
import array
import struct
import random

GENOME_STRUCT = ">??BBff"
GENOME_STRUCT_SIZE = struct.calcsize(GENOME_STRUCT)

def appropriate_genome_part_random(IC, NC, OC):
    return struct.pack(
        GENOME_STRUCT,
        random.randint(0, 5) > 4,
        random.randint(0, 5) > 4,
        random.randint(0, max(IC, NC)-1),
        random.randint(0, max(OC, NC)-1),
        random.uniform(-1.0, 1.0),
        random.uniform(-1.0, 1.0)
    )

class NN:
    def __init__(self, inputs: int = 0, outputs: int = 0, neurons: int = 2, genome: bytes = b""):
        self.inputs = array.array('f', [0.0 for _ in range(inputs)])
        self.outputs = array.array('f', [0.0 for _ in range(outputs)])
        self.genome = genome
        self.genome_decoded = []
        for x in range(0, len(genome), GENOME_STRUCT_SIZE):
            block = genome[x:x+GENOME_STRUCT_SIZE]
            self.genome_decoded.append(Connection(*struct.unpack(GENOME_STRUCT, block)))
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
                
                oval = ival*x.Weight + x.Bias
                
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
        if random.uniform(0.0, 1.0) < mutation:
            genome = self.genome
            for x in range(5):
                rindex = random.randint(0, len(genome)//GENOME_STRUCT_SIZE)*GENOME_STRUCT_SIZE
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
