import subprocess
import time
import re

def test_lt():
    print("Testing localtunnel...")
    process = subprocess.Popen(
        ['npx', '-y', 'localtunnel', '--port', '8000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )
    
    time.sleep(5)
    process.terminate()
    stdout, stderr = process.communicate()
    print("STDOUT:", stdout)
    print("STDERR:", stderr)

if __name__ == "__main__":
    test_lt()
