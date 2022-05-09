import os
import argparse
import time
import multiprocessing

parser = argparse.ArgumentParser()
parser.add_argument("trainoutdir", metavar="DIRECTORY", default=".", help="Output Directory to spit out simulation data", nargs="?")
parser.add_argument("-v", "--view", help="View the simulation as it trains", action="store_true")
parser.add_argument("-i", "--iterations", help="Number of iterations to train for", type=int)
parser.add_argument("-s", "--start-count", help="Starting Count", default=1, type=int)
parser.add_argument("-p", "--prefix", help="Output file prefix before the train count", default="simdata")
args = parser.parse_args()

if not os.path.exists(args.trainoutdir):
    os.mkdir(args.trainoutdir)

def background_train(args):
    for x in range(args.start_count, args.start_count + args.iterations):
        print(f"\n\nTRAIN ATTEMPT: {x}")
        os.system(f'python nnsim.py selected.pickle -o "{args.trainoutdir}/{args.prefix}{x}.pickle"')

trainer = multiprocessing.Process(target=background_train, daemon=False, name="Trainer", args=(args,))
trainer.start()

try:
    if args.view:
        for x in range(args.start_count, args.start_count + args.iterations):
            while not os.path.exists(f"{args.trainoutdir}/{args.prefix}{x}.pickle"):
                time.sleep(0.2)
            os.system(f'python view.py "{args.trainoutdir}/{args.prefix}{x}.pickle" -u')
except KeyboardInterrupt:
    trainer.kill()
    import sys
    sys.exit()

try:
    trainer.join()
except KeyboardInterrupt:
    trainer.kill()
    import sys
    sys.exit()
