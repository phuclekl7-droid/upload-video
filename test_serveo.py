import subprocess
import re
import time

def test_serveo():
    print("Testing serveo tunnel...")
    process = subprocess.Popen(
        ['ssh', '-o', 'StrictHostKeyChecking=no', '-R', '80:localhost:8000', 'serveo.net'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(5)
    
    # Read output
    process.terminate()
    stdout, stderr = process.communicate()
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
    
    print("Done testing.")

if __name__ == "__main__":
    test_serveo()
