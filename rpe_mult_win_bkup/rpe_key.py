import argparse
from psychopy import visual, core, event
import numpy as np
from pynput import mouse as pynput_mouse  # Rename the pynput mouse module
import threading
import time

# Add argument parser
parser = argparse.ArgumentParser(description='RPE Rating Task')
parser.add_argument('--full',
                   action='store_true',
                   help='Show all questions. If not set, only shows RPE and Arousal questions.')
parser.add_argument('--windowed', 
                   action='store_true', 
                   help='Run in windowed mode (default is fullscreen).')
args = parser.parse_args()

# Define dictionaries for different scales
rpe_dict = {-5:'Very Bad', -4:'', -3:'Bad', -2:'', -1:'Fairly Bad', 0:'', 
            1:'Fairly Good', 2:'', 3:'Good', 4:'', 5:'Very Good'}
arousal_dict = {1:'Low Arousal', 2:'', 3:'', 4:'', 5:'', 6:'High Arousal'}
agreement_dict = {1:'Strongly Disagree', 2:'Disagree', 3:'Neutral', 4:'Agree', 5:'Strongly Agree'}

# Define titles and their associated dictionaries and questions
titles = {
    'RPE': [rpe_dict, {'affect': 'Please indicate the response that describes how you feel right now'}],
    'By "arousal" here is meant how "worked up" you feel. You might experience high arousal in one of a variety of ways, for example, as excitement or anxiety or anger. Low arousal might also be experienced by you in one of a number of different ways, for example as relaxation or boredom or calmness.': [arousal_dict, {'arousal': 'Please indicate the response that describes best your level of arousal right now'}],
    'Please indicate how much you agree with the following statements': [agreement_dict, {
        'cog_appraisal_a': 'I feel confident that I will be able to complete the exercise session',
        'cog_appraisal_b': 'I feel comfortable continuing to bike at this intensity',
        'cog_appraisal_c': 'I am thinking about the health benefits of my exercising',
        'cog_appraisal_d': 'I am enjoying the exercise',
        'cog_appraisal_e': 'I feel a sense of achievement engaging in this exercise',
        'cog_appraisal_f': "I am focused on my body's response to biking",
        'cog_appraisal_g': 'I feel like time is passing',
        'cog_appraisal_h': 'I think experiencing some breathlessness, muscle pain, or heart pounding indicates that this biking is good for me'
    }]
}

def create_page(win1, win2, title, subtitle, value_dict, full):
    """Create a page with title, subtitle, and slider based on the value dictionary"""
    # Create title text for both windows (adjusted size and position)
    title_text1 = visual.TextStim(win=win1, text='', pos=(0, 0.4), height=0.04)
    title_text2 = visual.TextStim(win=win2, text=title, pos=(0, 0.1), height=0.05, wrapWidth=1.6)
    
    # Create subtitle text for both windows (adjusted size and position)
    subtitle_text1 = visual.TextStim(win=win1, text='', pos=(0, 0.28), height=0.035, wrapWidth=0.8)
    subtitle_text2 = visual.TextStim(win=win2, text=subtitle, pos=(0, -0.4), height=0.06, wrapWidth=1.6)
    
    # Get tick values for this page's scale
    tick_values = sorted(list(value_dict.keys()))
    
    # Create slider with values from dictionary for both windows (doubled size)
    slider1 = visual.Slider(win=win1, size=(1.2, 0.1), pos=(0, 0.1), units='height', ticks=tick_values,
                            labels=None, granularity=1.0, style='rating', color='white',
                            fillColor='red', borderColor='white', labelHeight=0.1)
    
    slider2 = visual.Slider(win=win2, size=(0, 0), pos=(0, 0), units='height', ticks=tick_values,
                            labels=None, granularity=1.0, style='rating', color='white',
                            fillColor='red', borderColor='white', labelHeight=0.1)
    
    # Create tick labels and description labels for both windows
    tick_labels1, tick_labels2, description_labels1, description_labels2 = [], [], [], []
    
    for value in tick_values:
        norm_pos = ((value - tick_values[0]) / (tick_values[-1] - tick_values[0]) - 0.5) * slider1.size[0]
        
        # Create value label above the slider (doubled size)
        value_label1 = visual.TextStim(win=win1, text=str(value), pos=(norm_pos, 0.2), height=0.06, anchorHoriz='center', wrapWidth=0.2)
        tick_labels1.append(value_label1)
        
        value_label2 = visual.TextStim(win=win2, text='', pos=(norm_pos, 0.1), height=0.06, anchorHoriz='center', wrapWidth=0.2)
        tick_labels2.append(value_label2)
        
        # Create description label below the slider (doubled size)
        if value_dict[value]:
            description_label1 = visual.TextStim(win=win1, text=value_dict[value], pos=(norm_pos, -0.05), height=0.05, anchorHoriz='center', wrapWidth=0.2)
            description_labels1.append(description_label1)
            
            description_label2 = visual.TextStim(win=win2, text='', pos=(norm_pos, -0.15), height=0.05, anchorHoriz='center', wrapWidth=0.2)
            description_labels2.append(description_label2)

    # Create value display and response display for both windows
    value_display1 = visual.TextStim(win=win1, text='Use Left/Right buttons to move, Middle button to select', pos=(0, -0.3), height=0.05)
    value_display2 = visual.TextStim(win=win2, text='', pos=(0, -0.3), height=0.05)
    
    response_display1 = visual.TextStim(win=win1, text='', pos=(0, -0.4), height=0.05, color='green')
    response_display2 = visual.TextStim(win=win2, text='', pos=(0, -0.1), height=0.05, color='green')
    
    return (title_text1, subtitle_text1, slider1, value_display1, response_display1, tick_labels1, description_labels1), \
           (title_text2, subtitle_text2, slider2, value_display2, response_display2, tick_labels2, description_labels2)

def run_rpe(win1=None, win2=None, full=False, outlet=None):
    """Run the RPE assessment
    
    Args:
        win1: psychopy window object for the first window. If None, creates new window
        win2: psychopy window object for the second window. If None, creates new window
        full: boolean to determine if full questionnaire is shown
        outlet: LSL outlet for sending markers. If None, no markers are sent
    Returns:
        dict: responses from the assessment
    """
    # Create windows if not provided
    if win1 is None:
        win1 = visual.Window(size=(1024, 768), units='height', fullscr=True, color='gray')
    if win2 is None:
        win2 = visual.Window(size=(1024, 768), units='height', fullscr=True, color='gray')

    # Create mouse object
    mouse_controller = event.Mouse()

    # Function to continuously reset mouse position
    def lock_mouse_position():
        while True:
            mouse_controller.setPos((win1.size[0] // 2, win1.size[1] // 2))  # Lock to center of the window
            time.sleep(0.01)  # Sleep briefly to reduce CPU usage

    # Start the thread to lock mouse position
    mouse_lock_thread = threading.Thread(target=lock_mouse_position, daemon=True)
    mouse_lock_thread.start()

    # Initialize dictionary to store all responses
    all_responses = {}

    # Loop through each title and its pages
    for title, (value_dict, subtitles) in titles.items():
        response_text = ""  # Reset response_text for each page
        if title == 'RPE':
            title = ''
        # Skip agreement questions if full is False
        if not full and title == 'Please indicate how much you agree with the following statements':
            continue
            
        for subtitle_key, subtitle_value in subtitles.items():  # Iterate over the dictionary
            response_text = ""  # Reset response_text for each subtitle
            # Create page elements
            (title_text1, subtitle_text1, slider1, value_display1, response_display1, tick_labels1, description_labels1), \
             (title_text2, subtitle_text2, slider2, value_display2, response_display2, tick_labels2, description_labels2) = create_page(
                win1, win2, title, subtitle_value, value_dict, full
            )
            
            response = None
            # Initialize current value to middle tick mark
            tick_values = sorted(list(value_dict.keys()))
            middle_index = len(tick_values) // 2
            current_value = tick_values[middle_index]
            
            last_left_click = False
            last_right_click = False
            last_middle_click = False  # Track the state of the middle mouse button

            # Set up pynput listener for mouse buttons
            def on_click(x, y, button, pressed):
                nonlocal current_value, all_responses, subtitle_key, response_text
                if pressed:
                    if button == pynput_mouse.Button.middle or button == pynput_mouse.Button.x1:  # Check for middle button or XButton1
                        # Format response as key=value
                        key_response = f"{subtitle_key}={int(current_value)}"  # Use subtitle_key for the response
                        all_responses[key_response] = current_value
                        
                        # Store the response text to be updated in the main loop
                        response_text = f"Response: {int(current_value)}"

            # Start the mouse listener
            listener = pynput_mouse.Listener(on_click=on_click)
            listener.start()

            while True:
                # Check for escape key to exit RPE assessment
                keys = event.getKeys()
                if 'escape' in keys or 'enter' in keys or 'return' in keys:  # If escape key is pressed
                    listener.stop()  # Stop the listener
                    return True  # Return None to indicate termination of RPE assessment

                # Find current index in tick values
                current_index = tick_values.index(current_value)

                # Handle mouse input
                mouse_event = event.Mouse(win=win1)
                mouse_x, mouse_y = mouse_event.getPos()
                left_click = mouse_event.getPressed()[0]  # Left mouse button
                middle_click = mouse_event.getPressed()[1]  # Middle mouse button
                right_click = mouse_event.getPressed()[2]  # Right mouse button
                
                # Move left on left click (only if it was not previously clicked)
                if left_click and not last_left_click:  
                    if current_index > 0:
                        current_value = tick_values[current_index - 1]
                last_left_click = left_click  # Update the last left click state

                # Move right on right click (only if it was not previously clicked)
                if right_click and not last_right_click:  
                    if current_index < len(tick_values) - 1:
                        current_value = tick_values[current_index + 1]
                last_right_click = right_click  # Update the last right click state

                # Check for spacebar to progress to the next question
                if 'space' in keys and response_text:  # Ensure a response has been recorded
                    outlet.push_sample([f'{subtitle_text1}_{response_text}'])
                    break  # Exit the loop to proceed to the next screen
                
                last_middle_click = middle_click  # Update the last middle click state

                # Update slider and position indicator
                slider1.rating = current_value
                slider1.setTicks(tick_values)  # Ensure the ticks are set to the keys of the value_dict
                
                # Draw everything on both windows
                title_text1.draw()
                subtitle_text1.draw()
                slider1.draw()
                value_display1.draw()
                response_display1.draw()
                
                # Draw tick labels and descriptions for win1
                for label in tick_labels1:
                    label.draw()
                for desc_label in description_labels1:
                    desc_label.draw()
                
                title_text2.draw()
                subtitle_text2.draw()
                slider2.draw()
                value_display2.draw()
                response_display2.draw()
                
                # Draw tick labels and descriptions for win2
                for label in tick_labels2:
                    label.draw()
                for desc_label in description_labels2:
                    desc_label.draw()
                
                # Update the response display text
                response_display2.text = response_text  # Update the response display text
                
                win1.flip()  # Draw on the first window
                win2.flip()  # Draw on the second window

            # Stop the listener after exiting the loop
            listener.stop()

    return all_responses

def main():
    """Main function when running as script"""
    parser = argparse.ArgumentParser(description='RPE Rating Task')
    parser.add_argument('--full',
                       action='store_true',
                       help='Show all questions. If not set, only shows RPE and Arousal questions.')
    parser.add_argument('--windowed', 
                       action='store_true', 
                       help='Run in windowed mode (default is fullscreen).')
    args = parser.parse_args()
    
    responses = run_rpe(full=args.full)
    
    # Print all responses
    print("\nAll responses:")
    for question, response in responses.items():
        print(f"{question}: {int(response)}")

if __name__ == "__main__":
    main() 