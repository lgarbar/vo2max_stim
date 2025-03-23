# README for RPE Experiment

## Overview

This repository contains code for conducting a Rating of Perceived Exertion (RPE) experiment using PsychoPy and the Lab Streaming Layer (LSL) for real-time data streaming. The experiment is designed to assess participants' perceived exertion during various exercise intervals, including warm-up, VO2Max, and cool-down phases.

## Folder Structure

- `rpe_key.py`: Contains the logic for running the RPE assessment, including mouse input handling and response recording.
- `rpe_accel.py`: Implements a continuous RPE rating task with a slider interface, allowing participants to provide real-time feedback on their exertion levels.
- `vo2max.py`: Manages the overall experiment flow, including displaying screens, timing sequences, and integrating RPE assessments into the VO2Max protocol.

## Requirements

To run the experiment, ensure you have the following installed:

- Python 3.x
- PsychoPy
- pylsl
- numpy

You can install the required packages using pip:

```bash
pip install psychopy pylsl numpy
```


## Running the Experiment

To run the experiment, execute the `vo2max.py` script. You can specify the monitor to use by adjusting the `screen` parameter in the script.

```bash
python vo2max.py
```


### Command-Line Arguments

#### rpe_key.py
- `--full`: Show all questions in the RPE assessment. If not set, only RPE and Arousal questions will be shown.
- `--windowed`: Run the experiment in windowed mode. By default, the experiment runs in fullscreen mode.

#### vo2max.py
- `--windowed`: Run the experiment in windowed mode. By default, the experiment runs in fullscreen mode.


## Experiment Flow

1. **Initial Screens**: Displays waiting messages before the experiment begins.
2. **RPE Assessment**: Participants provide their perceived exertion ratings using mouse clicks.
3. **Rest and Warmup Screens**: Displays messages during rest and warmup phases.
4. **VO2Max Sequence**: Conducts the VO2Max test with timed RPE assessments.
5. **Cool Down Phase**: Displays a countdown timer for the cool-down phase, updating every minute with a message to record heart rate in REDCap.
6. **Final Screens**: Displays messages after the experiment concludes.

## Data Collection

Responses from the RPE assessments are collected and can be printed to the console at the end of the experiment. The data can also be streamed using LSL for real-time analysis.

## Multiple Screen Support

The experiment supports multiple screens, allowing for a more flexible setup. The RPE assessments and other stimuli can be displayed on different monitors as specified in the code.

## Cleanup

The `cleanup` method ensures that the PsychoPy window is closed and the program exits cleanly after the experiment is finished.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments

This experiment is based on the principles of exercise physiology and the RPE scale developed by Borg. Special thanks to the PsychoPy community for their support and resources.

