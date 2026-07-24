import subprocess
import re
import time

def test_localhost_run():
    print("Testing localhost.run tunnel...")
    process = subprocess.Popen(
        ['ssh', '-o', 'StrictHostKeyChecking=no', '-R', '80:localhost:8000', 'nokey@localhost.run'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(10)
    process.terminate()
    stdout, stderr = process.communicate()
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
    
    print("Done testing.")

if __name__ == "__main__":
    test_localhost_run()
