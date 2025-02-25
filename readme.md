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

- `--full`: Show all questions in the RPE assessment. If not set, only RPE and Arousal questions will be shown.
- `--continuous`: Allow continuous values for the RPE rating. If not set, only discrete values from the tick marks are allowed.

## Experiment Flow

1. **Initial Screens**: Displays waiting messages before the experiment begins.
2. **RPE Assessment**: Participants provide their perceived exertion ratings using mouse clicks.
3. **Rest and Warmup Screens**: Displays messages during rest and warmup phases.
4. **VO2Max Sequence**: Conducts the VO2Max test with timed RPE assessments.
5. **Final Screens**: Displays messages after the experiment concludes.

## Data Collection

Responses from the RPE assessments are collected and can be printed to the console at the end of the experiment. The data can also be streamed using LSL for real-time analysis.

## Cleanup

The `cleanup` method ensures that the PsychoPy window is closed and the program exits cleanly after the experiment is finished.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments

This experiment is based on the principles of exercise physiology and the RPE scale developed by Borg. Special thanks to the PsychoPy community for their support and resources.

