import os
from psychopy import visual, core

win = visual.Window(
    size=(800, 600),
    color='black',
    fullscr=False,
    units='height'
)

trigger_path = 'testing/trigger.txt'
last_trigger = ""
stimuli = ["Hello there!", "Get ready...", "This is a test.", "You're doing great!", "Bye 👋"]

for text in stimuli:
    message = visual.TextStim(win, text=text, color='white', height=0.1)
    message.draw()
    win.flip()

    while True:
        if os.path.exists(trigger_path):
            with open(trigger_path, 'r') as f:
                contents = f.read().strip()

            if contents and contents != last_trigger:
                if 'space' in contents:
                    last_trigger = contents
                    print("Trigger received!")
                    with open(trigger_path, 'w') as f:
                        f.write('')
                    break

win.close()
core.quit()
