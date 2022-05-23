import sys
import subprocess
sys.path.append("../simulator-knx/simulator")
from simulator import launch_simulation #simulator.


if __name__ == "__main__":
    # Windows
    # subprocess.call('start /wait python bb.py', shell=True)
    # Mac OS
    subprocess.call(['open', '-W', '-a', 'Terminal.app', 'python', '--args', 'bb.py'])
    # Linux
    # subprocess.call(['xterm', '-e', 'python bb.py'])
    launch_simulation()