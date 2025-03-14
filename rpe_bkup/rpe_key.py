import argparse
from psychopy import visual, core, event
import numpy as np

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
titles = {'RPE':
            [rpe_dict, 
             {'affect':'Please indicate the response that describes how you feel right now'}
             ],
          'Arousal':
            [arousal_dict, 
             {'arousal':'Please indicate the response that describes best your level of arousal right now'}
             ],
          'Please indicate how much you agree with the following statements':
            [agreement_dict,
             {'cog_appraisal_a':'I feel confident that I will be able to complete the exercise session',
             'cog_appraisal_b':'I feel comfortable continuing to bike at this intensity',
             'cog_appraisal_c':'I am thinking about the health benefits of my exercising',
             'cog_appraisal_d':'I am enjoying the exercise',
             'cog_appraisal_e':'I feel a sense of achievement engaging in this exercise',
             'cog_appraisal_f':"I am focused on my body's response to biking",
             'cog_appraisal_g':'I feel like time is passing',
             'cog_appraisal_h':'I think experiencing some breathlessness, muscle pain, or heart pounding indicates that this biking is good for me'}
             ]
          }

def create_page(win, title, subtitle, value_dict, full):
    """Create a page with title, subtitle, and slider based on the value dictionary"""
    # Create title text
    title_text = visual.TextStim(
        win=win,
        text=title,
        pos=(0, 0.4),
        height=0.06
    )
    
    # Create subtitle text
    subtitle_text = visual.TextStim(
        win=win,
        text=subtitle,
        pos=(0, 0.2),
        height=0.05,
        wrapWidth=0.8
    )
    
    # Get tick values for this page's scale
    tick_values = sorted(list(value_dict.keys()))
    
    # Create slider with values from dictionary
    slider = visual.Slider(
        win=win,
        size=(0.8, 0.05),
        pos=(0, 0),
        units='height',
        ticks=tick_values,  # Set ticks based on the keys of the value_dict
        labels=None,  # Set labels to None as we will display numbers above the scale
        granularity=1.0,
        style='rating',
        color='white',
        fillColor='red',
        borderColor='white',
        labelHeight=0.05
    )
    
    # Create position indicator (only one red dot)
    position_indicator = visual.Circle(
        win=win,
        radius=0.015,  # Made slightly larger for better visibility
        fillColor='red',
        lineColor='red',
        pos=(0, slider.pos[1])
    )
    
    # Create label display for tick marks with adjusted positions
    tick_labels = []
    description_labels = []  # New list for description labels
    slider_range = tick_values[-1] - tick_values[0]
    for value in tick_values:
        norm_pos = ((value - tick_values[0]) / slider_range - 0.5) * slider.size[0]
        value_label = visual.TextStim(
                win=win,
                text=str(value),  # Use the value itself as the label
                pos=(norm_pos, 0.05),  # Position above the slider
                height=0.03,
                anchorHoriz='center',
                wrapWidth=0.2
            )
        tick_labels.append(value_label)
        if value_dict[value]:
            # Create label for the description below the slider
            description_label = visual.TextStim(
                win=win,
                text=value_dict[value],  # Use the description from the dictionary
                pos=(norm_pos, -0.1),  # Position below the slider
                height=0.03,
                anchorHoriz='center',
                wrapWidth=0.2
            )
            description_labels.append(description_label)
    
    # Create value display and response display
    if not args.full or not full:
        value_text = 'Use Left/Right buttons to move, Middle button to select'
    else:
        value_text = ''
    print(value_text,(args.full, full))

    value_display = visual.TextStim(
            win=win,
            text=value_text,
            pos=(0, -0.2),
            height=0.05
        )
    
    response_display = visual.TextStim(
        win=win,
        text='',
        pos=(0, -0.3),
        height=0.05,
        color='green'
    )
    
    # Remove the second red dot (position indicator)
    position_indicator = visual.Circle(
        win=win,
        radius=0.015,  # Made slightly larger for better visibility
        fillColor='red',
        lineColor='red',
        pos=(0, slider.pos[1])  # Keep the position indicator at the slider's position
    )
    
    return title_text, subtitle_text, slider, tick_labels, description_labels, value_display, response_display, position_indicator

def run_rpe(win=None, full=False, outlet=None):
    global args
    """Run the RPE assessment
    
    Args:
        win: psychopy window object. If None, creates new window
        full: boolean to determine if full questionnaire is shown
        outlet: LSL outlet for sending markers. If None, no markers are sent
    Returns:
        dict: responses from the assessment
    """
    # Create window if not provided
    should_close_win = False
    args.full = full
    if win is None:
        win = visual.Window(
            size=(1024, 768),
            units='height',
            fullscr=not args.windowed,  # Use windowed argument to determine fullscreen
            color='gray'
        )
        should_close_win = True

    # Initialize dictionary to store all responses
    all_responses = {}

    # Loop through each title and its pages
    i = 0
    for title, (value_dict, subtitles) in titles.items():
        if title == 'RPE' or title == 'Arousal':
            title = ''
        # Skip agreement questions if full is False
        if not full and title == 'Please indicate how much you agree with the following statements':
            continue
            
        for subtitle_key, subtitle_value in subtitles.items():  # Iterate over the dictionary
            # Create page elements
            title_text, subtitle_text, slider, tick_labels, description_labels, value_display, response_display, position_indicator = create_page(
                win, title, subtitle_value, value_dict, full
            )
            
            response = None
            # Initialize current value to middle tick mark
            tick_values = sorted(list(value_dict.keys()))
            middle_index = len(tick_values) // 2
            current_value = tick_values[middle_index]
            
            last_left_click = False
            last_right_click = False
            last_middle_click = False  # Track the state of the middle mouse button

            while True:
                # Find current index in tick values
                current_index = tick_values.index(current_value)

                # Handle mouse input
                mouse = event.Mouse(win=win)
                mouse_x, mouse_y = mouse.getPos()
                left_click = mouse.getPressed()[0]  # Left mouse button
                right_click = mouse.getPressed()[2]  # Right mouse button
                middle_click = mouse.getPressed()[1]  # Middle mouse button

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

                # Handle response submission
                if middle_click and not last_middle_click:  # Submit response only if it was not previously clicked
                    # Format response as key=value
                    key_response = f"{subtitle_key}={int(current_value)}"  # Use subtitle_key for the response
                    all_responses[key_response] = current_value
                    
                    # Send LSL marker if outlet provided
                    if outlet:
                        outlet.push_sample([f'RPE_{key_response}'])
                    
                    i += 1  # Move to the next question
                    # Wait until the middle button is released before allowing another submission
                    while middle_click:  # Wait for the button to be released
                        middle_click = mouse.getPressed()[1]  # Update the state of the middle button
                    break  # Exit the loop to proceed to the next screen
                
                last_middle_click = middle_click  # Update the last middle click state

                # Update slider and position indicator
                slider.rating = current_value
                slider.setTicks(tick_values)  # Ensure the ticks are set to the keys of the value_dict
                
                # Calculate position for indicator
                slider_range = tick_values[-1] - tick_values[0]
                norm_pos = ((current_value - tick_values[0]) / slider_range - 0.5) * slider.size[0]
                position_indicator.pos = (norm_pos, slider.pos[1])
                
                # Update value display
                # value_display.text = f'Current value: {int(current_value)}'  # Removed current value display
                
                # Draw everything
                title_text.draw()
                subtitle_text.draw()
                slider.draw()
                for label in tick_labels:
                    label.draw()  # Draw value labels above the slider
                for desc_label in description_labels:
                    desc_label.draw()  # Draw description labels below the slider
                value_display.draw()
                response_display.draw()
                position_indicator.draw()
                win.flip()

    # Close window if we created it
    if should_close_win:
        win.close()

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