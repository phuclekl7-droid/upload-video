import subprocess
import re
import time
import threading

def test_pinggy():
    print("Testing pinggy tunnel...")
    process = subprocess.Popen(
        ['ssh', '-p', '443', '-R0:localhost:8000', '-o', 'StrictHostKeyChecking=no', 'a.pinggy.io'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    output = []
    def read_stdout():
        for line in process.stdout:
            output.append(line)
            print("STDOUT:", line.strip())
            
    t = threading.Thread(target=read_stdout)
    t.daemon = True
    t.start()
    
    time.sleep(10)
    process.terminate()
    
    print("Done testing.")

if __name__ == "__main__":
    test_pinggy()
