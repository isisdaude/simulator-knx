import sys
sys.path.append("../simulator-knx/simulator")
from simulator import launch_simulation


if __name__ == "__main__":
    # for a in sys.argv:
    #     print(a)
    launch_simulation(sys.argv)
    ## CLI arguments in sys.argv