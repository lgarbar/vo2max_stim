import tkinter as tk
from tkinter import ttk
from datetime import datetime
import subprocess
import configparser
import os

def ensure_config_exists():
    """Create config.ini if it doesn't exist"""
    config = configparser.ConfigParser()
    
    # Check if config file exists
    if not os.path.exists('config.ini'):
        # Create default configuration
        config['Tasks'] = {
            'available_tasks': 'rpe, other_task_1, other_task_2'
        }
        
        # Write to config file
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

def load_tasks():
    """Load available tasks from config.ini"""
    # Ensure config file exists
    ensure_config_exists()
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Get tasks and clean up any whitespace
    tasks_string = config.get('Tasks', 'available_tasks')
    tasks = [task.strip() for task in tasks_string.split(',') if task.strip()]
    return tasks

class StartupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Startup")
        
        # Load tasks from config
        self.tasks = load_tasks()
        
        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Participant Name
        ttk.Label(main_frame, text="Participant Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.participant_name = ttk.Entry(main_frame, width=30)
        self.participant_name.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Date (auto-filled with today's date)
        ttk.Label(main_frame, text="Date:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.date_entry = ttk.Entry(main_frame, textvariable=self.date_var, width=30)
        self.date_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Task Selection
        ttk.Label(main_frame, text="Task:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.task_var = tk.StringVar()
        self.task_dropdown = ttk.Combobox(main_frame, 
                                        textvariable=self.task_var,
                                        values=self.tasks,
                                        width=27,
                                        state='readonly')
        self.task_dropdown.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Continue Button
        self.continue_btn = ttk.Button(main_frame, 
                                     text="Continue",
                                     command=self.start_task)
        self.continue_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Error Message Label
        self.error_label = ttk.Label(main_frame, 
                                   text="",
                                   foreground="red",
                                   wraplength=300)
        self.error_label.grid(row=4, column=0, columnspan=2)
        
        # Center the window
        self.root.update_idletasks()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = root.winfo_width()
        window_height = root.winfo_height()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"+{x}+{y}")
    
    def validate_inputs(self):
        """Validate all input fields"""
        if not self.participant_name.get().strip():
            self.error_label["text"] = "Please enter a participant name"
            return False
        
        if not self.date_var.get().strip():
            self.error_label["text"] = "Please enter a date"
            return False
        
        if not self.task_var.get():
            self.error_label["text"] = "Please select a task"
            return False
        
        self.error_label["text"] = ""
        return True
    
    def start_task(self):
        """Start the selected task if all inputs are valid"""
        if not self.validate_inputs():
            return
        
        # Get the selected task
        task = self.task_var.get()
        
        if task == 'rpe':
            try:
                # Run rpe.py using subprocess
                subprocess.run(['python', 'rpe.py'], check=True)
                self.root.destroy()  # Close GUI after successful task completion
            except subprocess.CalledProcessError as e:
                self.error_label["text"] = f"Error running task: {str(e)}"
        else:
            self.error_label["text"] = f"Task '{task}' not yet implemented"

def main():
    root = tk.Tk()
    app = StartupGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()