""" Program starting hook. """

import sys
from simulator import launch_simulation 
sys.path.append("./simulator")

if __name__ == "__main__":
    launch_simulation(sys.argv)