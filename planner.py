import tkinter as tk
from tkinter import simpledialog
from tkinter.ttk import *
#Planner V1
class WeeklyPlanner(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Weekly Planner")
        # self.geometry("800x450")

        self.task_id = 1  # To keep track of task IDs
        self.row_id = 1
        self.grid_widgets = {}  # To store widgets in the grid
        self.selected_widget = None
        self.offset_x = 0  # X offset for dragging
        self.offset_y = 0  # Y offset for dragging

        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', "Tasks"]
        self.time_slots = [f"{i}:00" for i in range(8, 16)]

        self.create_grid()
        self.create_task_management()

    def create_grid(self):
        # Create headers for days
        for col, day in enumerate(self.days):
            label = tk.Label(self, text=day, borderwidth=0, relief="solid", padx=10, pady=10)
            label.grid(row=0, column=col+1, sticky="nsew")
            self.line_style = Style()
            self.line_style.configure("Line.TSeparator", background="#ed3c16")
            if not col == 7:
                separator_v = Separator(self, orient="vertical", style='Line.TSeparator')
                separator_v.grid(row=0, column=col+1, rowspan=1, columnspan=2, sticky="ns")
            else:
                pass


        # Create grid cells
        for row in range(1, len(self.time_slots) + 1):
            for col in range(1, len(self.days) + 1):
                frame = tk.Frame(self, borderwidth=0, relief="solid", width=100, height=50)
                frame.grid(row=row, column=col, sticky="nsew")
                
                frame.bind("<Button-1>", self.on_frame_click)
                self.grid_widgets[(row, col)] = frame

                if col < len(self.days):
                    separator_v = Separator(self, orient="vertical", style='Line.TSeparator')
                    separator_v.grid(row=row, column=col, rowspan=1, columnspan=2, sticky="ns")
        
    def create_task_management(self):
        # Add button for creating new tasks
        add_task_button = tk.Button(self, text="Add New Task", command=self.add_new_task)
        add_task_button.grid(row=len(self.time_slots) + 1, column=0, columnspan=len(self.days) + 1)

    def add_new_task(self):
        # Ask the user for the task name
        task_name = simpledialog.askstring("New Task", "Enter task name:")
        if task_name:
            # Find the first available row in the last column ("Tasks" column)
            task_column = len(self.days)  # Last column for tasks
            for row in range(1, len(self.time_slots) + 1):
                
                if not self.grid_widgets[(row, task_column)].winfo_children():
                    self.create_task(task_name, (self.row_id, task_column))
                    break

    def create_task(self, task_name, grid_position):
        task = tk.Label(self, text=task_name, bg="lightyellow", padx=20, pady=10, wraplength=100, justify="left")
        counter = 0
        counter_all = 0
        label_locations_all = []
        label_locations = []
        i = 0
        for widget in self.winfo_children():
            counter_all += 1
        difference = counter_all - 137
        if difference == 0:
            task.place(in_=self.grid_widgets[grid_position], relheight=0.99, relwidth=0.97)
        else:
            for x in range(0,difference):
                if self.winfo_children()[136+x].place_info()["in"].grid_info()['column'] == 8:
                    fill_row = self.winfo_children()[136+x].place_info()["in"].grid_info()['row']
                    label_locations.append(fill_row)
        print(label_locations)

        for row in label_locations:
            for x in range(1,8):
                if not x in label_locations:
                    #task = tk.Label(self, text=task_name, bg="lightyellow", padx=20, pady=10, wraplength=100, justify="left")
                    task.place(in_=self.grid_widgets[x,8], relheight=0.99, relwidth=0.97)
                    break

        # Create a new task as a draggable label
        
        #
        task.bind("<Button-1>", self.on_task_click)
        task.bind("<B1-Motion>", self.on_task_drag)
        task.bind("<ButtonRelease-1>", self.on_task_release)
        self.task_id += 1
        task_height = int(len(task_name))
        font_size = int(task_height/11)
        task.configure(font=("Arial", 12 - font_size), wraplength=100)
                      


    def on_task_click(self, event):
        # Store the clicked widget and calculate the offset
        
        self.selected_widget = event.widget

        self.offset_x = self.selected_widget.winfo_x()
        self.offset_y = self.selected_widget.winfo_y()
        
        self.selected_widget.lift()
        #print(self.selected_widget.winfo_reqheight(), self.selected_widget.winfo_reqwidth())
        
    def on_task_drag(self, event):
        # Move the widget with the mouse, taking the offset into account
        x= self.winfo_pointerx()
        y= self.winfo_pointery()
       
        window_x, window_y = self.winfo_rootx(), self.winfo_rooty()


        self.selected_widget.place(x=x-window_x-self.offset_x, y=y-window_y-self.offset_y)

    def on_task_release(self, event):
        # Snap the widget to the closest grid cell
        closest_frame = self.get_closest_frame(event.x_root, event.y_root)
        if closest_frame:
            self.selected_widget.place_forget()  # Remove from the previous location
            self.selected_widget.place(in_=closest_frame, relwidth=0.99, relheight=0.97)  # Place in the new frame
        self.selected_widget = None

    def get_closest_frame(self, x_root, y_root):
        # Find the grid cell closest to the current mouse position
        for (row, col), frame in self.grid_widgets.items():
            if self.is_within_frame(frame, x_root, y_root):
                return frame
        return None

    def is_within_frame(self, frame, x_root, y_root):
        # Check if the given coordinates are within the frame
        x1 = frame.winfo_rootx()
        y1 = frame.winfo_rooty()
        x2 = x1 + frame.winfo_width()
        y2 = y1 + frame.winfo_height()
        return x1 <= x_root <= x2 and y1 <= y_root <= y2

    def on_frame_click(self, event):
        pass  # Optionally handle frame clicks

if __name__ == "__main__":
    app = WeeklyPlanner()
    app.mainloop()
