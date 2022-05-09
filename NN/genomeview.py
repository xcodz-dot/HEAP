from pyvis.network import Network
import nn
import struct
import webbrowser
import argparse
import pickle

def view(genome: bytes, inodes = [], onodes = [], bnodes = []):
    genome_decoded = []
    for x in range(0, len(genome), nn.GENOME_STRUCT_SIZE):
        block = genome[x:x+nn.GENOME_STRUCT_SIZE]
        genome_decoded.append(nn.Connection(*struct.unpack(nn.GENOME_STRUCT, block)))
    net = Network()
    oid = [f'o{x}' for x in range(len(onodes))]
    iid = [f'i{x}' for x in range(len(inodes))]
    bid = [f'n{x}' for x in range(len(bnodes))]
    aid=  oid + iid + bid
    net.add_nodes(iid, label=inodes)
    net.add_nodes(oid, label=onodes)
    net.add_nodes(bid, label=bnodes)

    for x in genome_decoded:
        src = ('i' if x.From else 'n')+str(x.NeuronIdIn)
        if src not in aid:
            continue
        to =  ('o' if x.To else 'n')+str(x.NeuronIdOut)
        if to not in aid:
            continue
        net.add_edge(src, to, physics=True, width=1+abs(x.Weight*10+x.Bias), color='red' if x.Weight < 0.0 else 'green')

    net.show_buttons()

    f = open("genome.html", 'w')
    f.write(net.generate_html())
    f.close()

    webbrowser.open_new_tab("genome.html")

parser = argparse.ArgumentParser()
parser.add_argument("index", help="Index to load from", type=int)
parser.add_argument("inodes", help="File with inode labels")
parser.add_argument("onodes", help="File with onode labels")
parser.add_argument("bnodes", type=int, help="Number of inbetween nodes")
parser.add_argument("file", help="File to read gnomes from", default="selected.pickle", nargs="?")
args = parser.parse_args()

inodes = open(args.inodes).read().splitlines()
onodes = open(args.onodes).read().splitlines()
bnodes = [f"N{x}" for x in range(args.bnodes)]

d = pickle.load(open(args.file, "rb"))[args.index]
view(d, inodes, onodes, bnodes)