import time
import keyboard
import os
import subprocess

trigger_path = 'testing/trigger.txt'

subprocess.run(['python', 'testing/test_1.py'])

while True:
    if keyboard.is_pressed('space'):
        with open(trigger_path, 'w') as f:
            f.write(f'space_{time.time()}')
        print("Trigger written.")
        time.sleep(0.3)
