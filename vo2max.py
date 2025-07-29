from psychopy import visual, core, event
import time
from pylsl import StreamInfo, StreamOutlet
from rpe_key import run_rpe
import argparse
import csv  # Add this import at the top
import threading

class ExperimentFlow:
    def __init__(self, screen=1, fullscreen=True, filename='data_log.csv'):  # Added filename parameter
        # Set up LSL stream
        self.info = StreamInfo('StimMarkers', 'Markers', 1, 0, 'string', 'uniqueid')
        self.outlet = StreamOutlet(self.info)
        self.terminate_requested = False
        
        # Create two windows based on fullscreen parameter
        self.win1 = visual.Window(
            size=(860, 480),
            units='height',
            fullscr=not args.windowed,  # Use windowed argument to determine fullscreen
            screen=2,  # Use second monitor
            color='gray'
        )
        
        self.win2 = visual.Window(
            size=(860, 480),
            units='height',
            fullscr=not args.windowed,  # Use windowed argument to determine fullscreen
            screen=0,  # Use primary monitor
            color='gray'
        )
        
        # Create text stimulus for both windows
        self.text_stim1 = visual.TextStim(
            win=self.win1,
            text='',
            height=0.05,
            wrapWidth=0.8
        )
        
        self.text_stim2 = visual.TextStim(
            win=self.win2,
            text='',
            height=0.05,
            wrapWidth=0.8
        )
        
        # VO2Max timing sequence (in seconds)
        self.vo2max_intervals = [1, 120, 360, 600, 840, 1080]

        # Dictionary for text mappings
        self.text_mapping = {
            "waiting_experiment": "Waiting for experiment to begin...",
            "waiting_init_rpe": "Waiting to begin first RPE",
            "waiting_rest": "Waiting to begin Rest",
            "rest": "Rest",
            "waiting_baseline": "Waiting to begin baseline collection",
            "baseline": "Collecting Baseline VO2 and HR",
            "warmup": "Warmup",
            "vo2max": "VO2Max",
            "cool_down": "Cool Down",
            "experiment_over": "The experiment is over. Thank you for your participation."
        }
        
        self.filename = filename  # Store the log filename
        self.setup_logging()  # Set up logging when initializing
        # Remove mouse_lock_active, mouse_lock_thread, and terminate_requested if only used for mouse lock

    def setup_logging(self):
        """Set up the CSV file for logging data."""
        self.log_file = open(self.filename, mode='w', newline='')
        self.csv_writer = csv.writer(self.log_file)
        self.csv_writer.writerow(['StimMarkersAlpha', 'Timestamp'])  # Write header row

    def log_data(self, data):
        """Log data to the CSV file."""
        self.csv_writer.writerow(data)  # Write timestamp and data to CSV

    def push_sample(self, data):
        """Push sample to LSL and log it."""
        self.outlet.push_sample(data)  # Original LSL push
        timestamp = time.time()
        self.log_data(data + [timestamp])  # Log the entire data array locally

    def show_screen(self, key, wait_for_space=True, duration=None):
        """Display screen with text and optionally wait for spacebar"""
        text = self.text_mapping[key]  # Get the text from the mapping
        self.text_stim1.text = ''
        self.text_stim2.text = text
        
        # Send LSL onset marker
        self.push_sample([f'{key}_onset'])  # Use the key for LSL onset marker

        if key == 'waiting_experiment':
            self.text_stim1.text = text
            self.text_stim2.text = text
        
        if key == 'experiment_over':
            self.text_stim1.text = text
            self.text_stim2.text = "Experiment Over.\n5 minutes have passed. Record HR in REDCap"
        if key == "cool_down":
            # Start the cool down timer
            start_time = time.time()
            elapsed_time = 0
            while elapsed_time < 300:  # 5 minutes = 300 seconds
                if self.terminate_requested:
                    return
                # Update the text stimulus for every minute
                minutes_passed = int(elapsed_time // 60)
                if 1 <= minutes_passed <= 5:  # Only show this message for the first 5 minutes
                    self.push_sample([f'{key}_{minutes_passed}_hr'])
                    if minutes_passed == 1:
                        self.text_stim2.text = f"Cool Down\n{minutes_passed} minute has passed. Record HR in REDCap"
                    else:
                        self.text_stim2.text = f"Cool Down\n{minutes_passed} minutes have passed. Record HR in REDCap"
                else:
                    self.text_stim2.text = "Cool Down"
                self.text_stim1.text = ""

                # Draw text stimuli in both windows
                self.text_stim1.draw()
                self.text_stim2.draw()
                self.win1.flip()
                self.win2.flip()

                # Check for spacebar to skip
                keys = event.getKeys(['space', 'escape'])
                if 'escape' in keys:
                    self.cleanup()
                    return
                if 'space' in keys and elapsed_time > 200:
                    break  # Skip to the next screen

                # Update elapsed time
                elapsed_time = time.time() - start_time
                core.wait(1)  # Wait for 1 second before the next update

            # After 5 minutes, transition to the experiment_over screen
            self.push_sample([f'cool_down_5_hr'])
            self.push_sample([f'{key}_offset'])  # Send LSL offset marker
            self.show_screen("experiment_over", wait_for_space=True)

        else:
            if duration:
                timer = core.CountdownTimer(duration)
                while timer.getTime() > 0:
                    if self.terminate_requested:
                        return
                    # Draw text stimuli in both windows
                    self.text_stim1.draw()
                    self.text_stim2.draw()
                    self.win1.flip()
                    self.win2.flip()
                    if event.getKeys(['escape']):
                        self.cleanup()
                        return
            else:
                while True:
                    if self.terminate_requested:
                        return
                    # Draw text stimuli in both windows
                    self.text_stim1.draw()
                    self.text_stim2.draw()
                    self.win1.flip()
                    self.win2.flip()
                    
                    keys = event.getKeys(['space', 'escape'])
                    if 'escape' in keys:
                        self.cleanup()
                        return
                    if wait_for_space and 'space' in keys:
                        # Check if the key contains 'waiting'
                        if 'waiting' not in key:
                            # Send LSL offset marker only if the key does not contain 'waiting'
                            self.push_sample([f'{key}_offset'])  # Use the key for LSL offset marker
                        break

    def run_rpe_assessment(self, full=False):
        """Run the RPE assessment using the imported function"""
        self.push_sample(['rpe_onset'])
        responses = run_rpe(win1=self.win1, win2=self.win2, full=full, outlet=self.outlet)  # Ensure both windows are passed
        for data in responses[1]:
            self.log_data(data)
        self.push_sample(['rpe_offset'])
        
        if responses is None:  # Check if the RPE assessment was terminated
            print("RPE assessment was terminated by the user.")
            return None  # Optionally return None or handle as needed

        return responses
    
    def vo2max_sequence(self):
        self.show_screen("warmup", duration=10)
        terminate = False
        self.push_sample(['vo2max_offset'])
        start_time = time.time()
        next_interval_idx = 0

        keys = event.getKeys(['space', 'escape', 'return', 'enter'])
        keys.remove('return') if 'return' in keys else keys

        while next_interval_idx < len(self.vo2max_intervals) and not terminate:
            if self.terminate_requested:
                return
            # Show VO2Max screen in both windows
            self.text_stim1.text = ""
            self.text_stim2.text = "VO2Max"
            self.text_stim1.draw()
            self.text_stim2.draw()
            self.win1.flip()
            self.win2.flip()

            keys = event.getKeys(['space', 'escape', 'return', 'enter'])
            if 'return' in keys or 'enter' in keys:
                terminate = True
            if 'escape' in keys:
                self.cleanup()
                return
            if 'space' in keys or terminate:
                self.push_sample(['vo2max_offset'])
                break

            # Check if it's time for RPE assessment
            current_time = time.time() - start_time + 10
            if next_interval_idx < len(self.vo2max_intervals) and current_time >= self.vo2max_intervals[next_interval_idx]:
                self.push_sample([f'rpe_assessment: {self.vo2max_intervals[next_interval_idx]}s'])
                terminate = self.run_rpe_assessment(full=True)
                terminate = terminate[0]
                next_interval_idx += 1

    def run_experiment(self):
        # Make the mouse invisible at the start of the experiment

        # # Initial screens
        # for key in ["waiting_experiment", "waiting_init_rpe"]:
        #     self.show_screen(key)

        # First RPE assessment
        # test = self.run_rpe_assessment()

        # # # Rest and Warmup screens
        # for key in ["waiting_rest", "rest", "waiting_baseline", "baseline"]:
        #     self.show_screen(key)

        # VO2Max sequence with timed RPE assessments
        self.vo2max_sequence()

        # Final screens
        for key in ["cool_down", "experiment_over"]:
            self.show_screen(key)

        self.cleanup()

    def cleanup(self):
        """Clean up and exit"""
        self.terminate_requested = True
        self.log_file.close()  # Close the log file
        self.win1.close()
        self.win2.close()
        core.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='VO2Max Experiment')
    parser.add_argument('--windowed', 
                        action='store_true', 
                        help='Run in windowed mode (default is fullscreen).')
    parser.add_argument('--filename', 
                        type=str, 
                        default='data_log.csv', 
                        help='Filename for logging data locally.')  # Added filename argument
    args = parser.parse_args()
    
    # Initialize with screen=1 for second monitor (adjust if needed)
    experiment = ExperimentFlow(screen=0, fullscreen=not args.windowed, filename=args.filename)  # Pass filename
    experiment.run_experiment()
