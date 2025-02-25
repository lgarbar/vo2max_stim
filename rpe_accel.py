import argparse
from psychopy import visual, core, event
import numpy as np

# Add argument parser
parser = argparse.ArgumentParser(description='RPE Rating Task')
parser.add_argument('--continuous', 
                   action='store_true',
                   help='Allow continuous values. If not set, only discrete values from the tick marks are allowed.')
parser.add_argument('--full',
                   action='store_true',
                   help='Show all questions. If not set, only shows RPE and Arousal questions.')
args = parser.parse_args()

rpe_dict = {-5:'Very Bad', -4:'', -3:'Bad', -2:'', -1:'Fairly Bad', 0:'', 
            1:'Fairly Good', 2:'', 3:'Good', 4:'', 5:'Very Good'}
arousal_dict = {1:'Low Arousal', 2:'', 3:'', 4:'', 5:'', 6:'High Arousal'}
agreement_dict = {1:'Strongly Disagree', 2:'Disagree', 3:'Neutral', 4:'Agree', 5:'Strongly Agree'}

titles = {'RPE':
            [rpe_dict, ['Please indicate the response that describes how you feel right now']],
          'Arousal':
            [arousal_dict, ['Please indicate the response that describes best your level of arousal right now']],
          'Please indicate how much you agree with the following statements':
            [agreement_dict,
             ['I feel confident that I will be able to complete the exercise session',
             'I feel comfortable continuing to bike at this intensity',
             'I am thinking about the health benefits of my exercising',
             'I am enjoying the exercise',
             'I feel a sense of achievement engaging in this exercise',
             "I am focused on my body's response to biking",
             'I feel like time is passing',
             'I think experiencing some breathlessness, muscle pain, or heart pounding indicates that this biking is good for me'
             ]]
          }

def create_page(win, title, subtitle, value_dict):
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
        pos=(0, 0.25),
        height=0.05,
        wrapWidth=0.8
    )
    
    # Create slider with values from dictionary
    slider = visual.Slider(
        win=win,
        size=(0.8, 0.05),
        pos=(0, 0),
        units='height',
        ticks=sorted(list(value_dict.keys())),  # Use dictionary keys as tick marks
        labels=None,
        granularity=0.1 if args.continuous else 1.0,
        style='rating',
        color='white',
        fillColor='red',
        borderColor='white',
        labelHeight=0.05
    )
    
    # Create red dot cursor
    cursor_dot = visual.Circle(
        win=win,
        radius=0.01,
        fillColor='red',
        lineColor='red',
        pos=(0, 0)
    )
    
    # Create label display for tick marks with adjusted positions
    tick_labels = []
    slider_range = slider.ticks[-1] - slider.ticks[0]
    for value in sorted(value_dict.keys()):
        if value_dict[value]:  # Only create labels for non-empty strings
            # Calculate normalized position (-0.4 to 0.4 for a slider of size 0.8)
            norm_pos = ((value - slider.ticks[0]) / slider_range - 0.5) * slider.size[0]
            label = visual.TextStim(
                win=win,
                text=value_dict[value],
                pos=(norm_pos, -0.1),  # Position relative to slider
                height=0.03,
                anchorHoriz='center',
                wrapWidth=0.2  # Prevent long labels from overlapping
            )
            tick_labels.append(label)
    
    # Create value display and response display
    value_display = visual.TextStim(
        win=win,
        text='Hover over the slider',
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
    
    return title_text, subtitle_text, slider, tick_labels, value_display, response_display, cursor_dot

# Create window
win = visual.Window(
    size=(1024, 768),
    units='height',
    fullscr=False,
    color='gray'
)

# Initialize dictionary to store all responses
all_responses = {}

# Loop through each title and its pages
i = 0
for title, (value_dict, subtitles) in titles.items():
    # Skip agreement questions if --full is not set
    if not args.full and title == 'Please indicate how much you agree with the following statements':
        continue
        
    for subtitle in subtitles:
        # Create page elements
        title_text, subtitle_text, slider, tick_labels, value_display, response_display, cursor_dot = create_page(
            win, title, subtitle, value_dict
        )
        
        response = None
        while True:
            mouse = event.Mouse(visible=False)  # Hide default cursor
            
            # Get mouse position and convert to slider value
            mouse_x = mouse.getPos()[0]
            slider_left = slider.pos[0] - slider.size[0]/2
            slider_right = slider.pos[0] + slider.size[0]/2
            
            # Calculate cursor position and value
            cursor_x = min(max(mouse_x, slider_left), slider_right)
            normalized_pos = (cursor_x - slider_left) / slider.size[0]
            hover_value = slider.ticks[0] + normalized_pos * (slider.ticks[-1] - slider.ticks[0])
            
            # Update cursor dot position
            cursor_dot.pos = (cursor_x, slider.pos[1])
            
            # Round the hover value if not continuous
            if not args.continuous and hover_value is not None:
                hover_value = round(hover_value)
            
            # Handle mouse click for recording response
            if mouse.getPressed()[0]:
                if hover_value is not None:
                    slider.rating = hover_value
                    response = hover_value
                    if args.continuous:
                        response_display.text = f'Response recorded: {response:.1f}'
                    else:
                        response_display.text = f'Response recorded: {int(response)}'
            
            # Update value display
            if hover_value is not None:
                if args.continuous:
                    value_display.text = f'Current value: {hover_value:.1f}'
                else:
                    value_display.text = f'Current value: {int(hover_value)}'
            
            # Draw everything
            title_text.draw()
            subtitle_text.draw()
            slider.draw()
            for label in tick_labels:
                label.draw()
            value_display.draw()
            response_display.draw()
            cursor_dot.draw()  # Draw the cursor dot
            win.flip()
            
            # Check for quit or next page
            keys = event.getKeys(['escape', 'q', 'space', 'n'])
            if 'escape' in keys or 'q' in keys:
                win.close()
                core.quit()
            elif ('space' in keys or 'n' in keys) and response is not None:
                # Store response and move to next page
                all_responses[f"Q{i}"] = response
                i += 1
                break

# Print all responses at the end
print("\nAll responses:")
for question, response in all_responses.items():
    if args.continuous:
        print(f"{question}: {response:.1f}")
    else:
        print(f"{question}: {int(response)}")

win.close()
core.quit()
