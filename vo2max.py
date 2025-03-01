from psychopy import visual, core, event
import time
from pylsl import StreamInfo, StreamOutlet
from rpe_key import run_rpe
import argparse

class ExperimentFlow:
    def __init__(self, screen=1, fullscreen=True):  # screen=1 for second monitor
        # Set up LSL stream
        self.info = StreamInfo('StimMarkers', 'Markers', 1, 0, 'string', 'uniqueid')
        self.outlet = StreamOutlet(self.info)
        
        # Create window based on fullscreen parameter
        self.win = visual.Window(
            size=(1024, 768),
            units='height',
            fullscr=not args.windowed,  # Use windowed argument to determine fullscreen
            screen=screen,  # Use specified monitor
            color='gray'
        )
        
        # Create text stimulus
        self.text_stim = visual.TextStim(
            win=self.win,
            text='',
            height=0.05,
            wrapWidth=0.8
        )
        
        # VO2Max timing sequence (in seconds)
        self.vo2max_intervals = [120, 360, 600, 840, 1080]

        # Dictionary for text mappings
        self.text_mapping = {
            "waiting_experiment": "Waiting for experiment to begin...",
            "waiting_init_rpe": "Waiting to begin first RPE",
            "waiting_rest": "Waiting to begin Rest",
            "rest": "Rest",
            "waiting_warmup": "Waiting to begin Warmup",
            "warmup": "Warmup",
            "vo2max": "VO2Max",
            "cool_down": "Cool Down",
            "experiment_over": "The experiment is over. Thank you for your participation."
        }
        
    def show_screen(self, key, wait_for_space=True, duration=None):
        """Display screen with text and optionally wait for spacebar"""
        text = self.text_mapping[key]  # Get the text from the mapping
        self.text_stim.text = text
        
        # Send LSL onset marker
        self.outlet.push_sample([f'{key}_onset'])  # Use the key for LSL onset marker
        
        if duration:
            timer = core.CountdownTimer(duration)
            while timer.getTime() > 0:
                self.text_stim.draw()
                self.win.flip()
                if event.getKeys(['escape']):
                    self.cleanup()
        else:
            while True:
                self.text_stim.draw()
                self.win.flip()
                
                keys = event.getKeys(['space', 'escape'])
                if 'escape' in keys:
                    self.cleanup()
                if wait_for_space and 'space' in keys:
                    # Check if the key contains 'waiting'
                    if 'waiting' not in key:
                        # Send LSL offset marker only if the key does not contain 'waiting'
                        self.outlet.push_sample([f'{key}_offset'])  # Use the key for LSL offset marker
                    break
    
    def run_rpe_assessment(self, full=False):
        """Run the RPE assessment using the imported function"""
        self.outlet.push_sample(['rpe_onset'])
        responses = run_rpe(win=self.win, full=full, outlet=self.outlet)
        self.outlet.push_sample(['rpe_offset'])
        return responses
    
    def vo2max_sequence(self):
        """Run the VO2Max sequence with timed RPE assessments"""
        self.outlet.push_sample(['vo2max_offset'])
        start_time = time.time()
        next_interval_idx = 0
        
        while next_interval_idx < len(self.vo2max_intervals):
            # Show VO2Max screen
            self.text_stim.text = "VO2Max"
            self.text_stim.draw()
            self.win.flip()
            
            # Check for spacebar to exit sequence
            keys = event.getKeys(['space', 'escape'])
            if 'escape' in keys:
                self.cleanup()
            if 'space' in keys:
                self.outlet.push_sample(['vo2max_offset'])
                break
            
            # Check if it's time for RPE assessment
            current_time = time.time() - start_time
            if next_interval_idx < len(self.vo2max_intervals) and current_time >= self.vo2max_intervals[next_interval_idx]:
                self.outlet.push_sample([f'rpe_assessment: {self.vo2max_intervals[next_interval_idx]}s'])
                self.run_rpe_assessment(full=True)
                next_interval_idx += 1
    
    def run_experiment(self):
        """Run the full experiment sequence"""
        # Initial screens
        for key in ["waiting_experiment", "waiting_init_rpe"]:
            self.show_screen(key)
        
        # First RPE assessment
        self.run_rpe_assessment(full=False)
        
        # Rest and Warmup screens
        for key in ["waiting_rest", "rest", "waiting_warmup", "warmup"]:
            self.show_screen(key)
        
        # VO2Max sequence with timed RPE assessments
        self.vo2max_sequence()
        
        # Final screens
        for key in ["cool_down", "experiment_over"]:
            self.show_screen(key)
        
        self.cleanup()
    
    def cleanup(self):
        """Clean up and exit"""
        self.win.close()
        core.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='VO2Max Experiment')
    parser.add_argument('--windowed', 
                        action='store_true', 
                        help='Run in windowed mode (default is fullscreen).')
    args = parser.parse_args()
    
    # Initialize with screen=1 for second monitor (adjust if needed)
    experiment = ExperimentFlow(screen=1, fullscreen=not args.windowed)
    experiment.run_experiment() 