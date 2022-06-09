""" Program starting hook. """

import sys
sys.path.append("./simulator")
from simulator import launch_simulation 

if __name__ == "__main__":
    launch_simulation(sys.argv)