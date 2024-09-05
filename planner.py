import tkinter as tk
from tkinter import simpledialog
from tkinter.ttk import *
import tkinter.font as tkFont
import datetime
import json
import os
#Planner V0.1.3
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
        self.initial_load()
        #print(self.winfo_children())

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
        global week_combobox
        global year_combobox
        # Add button for creating new tasks
        add_task_button = tk.Button(self, text="Add New Task", command=self.add_new_task)
        #add_task_button.grid(row=len(self.time_slots) + 1, column=0, columnspan=len(self.days) + 1)
        add_task_button.grid(row=len(self.time_slots) + 1, column=8)
        add_left_button = tk.Button(self, text="←", command=self.left_button)
        add_left_button.grid(row=len(self.time_slots) + 1, column=2, sticky="e")
        current_year = datetime.datetime.now().year
        total_weeks = datetime.date(current_year, 12, 28).isocalendar()[1]
        weeks = [f"Week {week}" for week in range(1, total_weeks + 1)]
        week_combobox = Combobox(self, values=weeks, width=10,state="readonly", postcommand=self.on_selection)
        week_combobox.grid(row=len(self.time_slots) + 1, column=3, columnspan=1)
        week_combobox.set(f"Week {datetime.datetime.now().isocalendar()[1]}") 
        week_combobox.bind("<<ComboboxSelected>>", self.on_week_combobox)
        add_right_button = tk.Button(self, text="→", command=self.right_button)
        add_right_button.grid(row=len(self.time_slots) + 1, column=4, sticky="w")
        add_save_button = tk.Button(self, text="Save", command=self.save)
        add_save_button.grid(row=len(self.time_slots) + 1, column=6)
        year_combobox = Combobox(self, values=["2024","2025","2026"], width=10,state="readonly", postcommand=self.on_selection)
        year_combobox.set(datetime.datetime.now().year)
        year_combobox.grid(row=len(self.time_slots) + 1, column=5)
        year_combobox.bind("<<ComboboxSelected>>", self.on_year_combobox)

    def on_selection(self):
        self.save()

    def on_week_combobox(self, event):
        counter = 0
        for widget in self.winfo_children():
            if widget.widgetName == "label":
                counter += 1
                if counter > 8:
                    widget.destroy()
        current_week = int(week_combobox.get().split(" ")[-1])
        current_year = int(year_combobox.get().split(" ")[-1])
        self.set_labels(current_week, current_year)

    def on_year_combobox(self, event):
        counter = 0
        for widget in self.winfo_children():
            if widget.widgetName == "label":
                counter += 1
                if counter > 8:
                    widget.destroy()
        current_year = int(year_combobox.get().split(" ")[-1])
        current_week = int(week_combobox.get().split(" ")[-1])
        self.set_labels(current_week, current_year)
        
    def set_labels(self, week, year):
        if os.path.exists("database\\{}-{}.txt".format(f"Week {week}", year)):
            with open("database\\{}-{}.txt".format(week_combobox.get(), year)) as load_file:
                date_array = json.load(load_file)
            for label in date_array:
                date_label = tk.Label(self, text=label[0], bg=label[2], padx=20, pady=10, wraplength=100, justify="center")
                date_label.place(in_=label[1], relheight=0.98, relwidth=0.99)
                task_height = int(len(label[0]))
                font_size = int(task_height/9)
                date_label.configure(font=("Arial", 12 - font_size), wraplength=100)
                current_font = tkFont.Font(font=date_label.cget("font"))
                if label[3] == 0:
                    current_font.configure(overstrike=False)
                else:
                    current_font.configure(overstrike=True)
                date_label.config(font=current_font)
                date_label.bind("<Button-1>", self.on_task_click)
                date_label.bind("<Button-3>", lambda event: self.on_right_click(event, date_label))
                date_label.bind("<B1-Motion>", self.on_task_drag)
                date_label.bind("<ButtonRelease-1>", self.on_task_release)
        else:
            pass

    def left_button(self):
        self.save()
        counter = 0
        for widget in self.winfo_children():
            if widget.widgetName == "label":
                counter += 1
                if counter > 8:
                    widget.destroy()
        pre_week = int(week_combobox.get().split(" ")[-1]) - 1
        week_combobox.set(f"Week {pre_week}")
        current_year = int(year_combobox.get().split(" ")[-1])
        self.set_labels(pre_week, current_year)

    def right_button(self):
        self.save()
        counter = 0
        for widget in self.winfo_children():
            if widget.widgetName == "label":
                counter += 1
                if counter > 8:
                    widget.destroy()
        next_week = int(week_combobox.get().split(" ")[-1]) + 1
        week_combobox.set(f"Week {next_week}")
        current_year = int(year_combobox.get().split(" ")[-1])
        self.set_labels(next_week, current_year)
                
    def save(self):
        
        widgets_all = []
        counter_label = 0
        for widget in self.winfo_children():
            if widget.widgetName == "label":
                counter_label += 1
                if counter_label > 8:
                    label_widgets = []
                    label_widgets.append(widget.cget("text"))
                    label_widgets.append(str(widget.place_info()["in"]))
                    label_widgets.append(widget.cget("bg"))
                    label_widgets.append(tkFont.Font(font=widget.cget("font")).cget("overstrike"))
                    widgets_all.append(label_widgets)
        with open("database\\{}-{}.txt".format(week_combobox.get(), year_combobox.get()),"w") as save_file:
            json.dump(widgets_all, save_file)

    def initial_load(self):
        if os.path.exists("database\\{}-{}.txt".format(f"Week {datetime.datetime.now().isocalendar()[1]}", datetime.datetime.now().year)):
            with open("database\\{}-{}.txt".format(f"Week {datetime.datetime.now().isocalendar()[1]}", datetime.datetime.now().year)) as load_file:
                initial_array = json.load(load_file)
            for label in initial_array:
                initial_label = tk.Label(self, text=label[0], bg=label[2], padx=20, pady=10, wraplength=100, justify="center")
                initial_label.place(in_=label[1], relheight=0.98, relwidth=0.99)
                task_height = int(len(label[0]))
                font_size = int(task_height/9)
                initial_label.configure(font=("Arial", 12 - font_size), wraplength=100)
                current_font = tkFont.Font(font=initial_label.cget("font"))
                if label[3] == 0:
                    current_font.configure(overstrike=False)
                else:
                    current_font.configure(overstrike=True)
                initial_label.config(font=current_font)
                initial_label.bind("<Button-1>", self.on_task_click)
                initial_label.bind("<Button-3>", lambda event: self.on_right_click(event, initial_label))
                initial_label.bind("<B1-Motion>", self.on_task_drag)
                initial_label.bind("<ButtonRelease-1>", self.on_task_release)
        else:
            pass

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
        for widget in self.winfo_children():
            if widget.widgetName == "menu":
                widget.destroy()
        task = tk.Label(self, text=task_name, bg="lightyellow", padx=20, pady=10, wraplength=100, justify="left")
        counter_all = 0
        label_locations = []
        i = 0
        #print(self.winfo_children())
        for widget in self.winfo_children():
            counter_all += 1
        difference = counter_all - 142
        if difference == 0:
            task.place(in_=self.grid_widgets[grid_position], relheight=0.99, relwidth=0.97)
        else:
            for x in range(0,difference):
                if self.winfo_children()[141+x].place_info()["in"].grid_info()['column'] == 8:
                    fill_row = self.winfo_children()[141+x].place_info()["in"].grid_info()['row']
                    label_locations.append(fill_row)
                else:
                    task.place(in_=self.grid_widgets[1,8], relheight=0.99, relwidth=0.97)

        for row in label_locations:
            for x in range(1,8):
                if not x in label_locations:
                    task.place(in_=self.grid_widgets[x,8], relheight=0.99, relwidth=0.97)
                    break

        # Create a new task as a draggable label
        
        #
        task.bind("<Button-1>", self.on_task_click)
        task.bind("<Button-3>", lambda event: self.on_right_click(event, task))
        task.bind("<B1-Motion>", self.on_task_drag)
        task.bind("<ButtonRelease-1>", self.on_task_release)
        self.task_id += 1
        task_height = int(len(task_name))
        font_size = int(task_height/9)
        task.configure(font=("Arial", 12 - font_size), wraplength=100)
                      

    def on_right_click(self,event, task):
        widget_under_mouse = self.winfo_containing(event.x_root, event.y_root)
        right_menu = tk.Menu(self, tearoff=0)
        category_menu = tk.Menu(right_menu, tearoff=0)
        right_menu.add_command(label="Set as Complete", command=lambda c="lightgray": self.select_complete(widget_under_mouse,c))
        right_menu.add_command(label="Set as Ongoing", command=lambda c="lightyellow": self.select_category(widget_under_mouse,c))
        category_menu.add_command(label="Urgent", command=lambda c="red": self.select_category(widget_under_mouse,c))
        category_menu.add_command(label="High", command=lambda c="OrangeRed2": self.select_category(widget_under_mouse,c))
        category_menu.add_command(label="Normal", command=lambda c="cyan2": self.select_category(widget_under_mouse,c))
        category_menu.add_command(label="Low", command=lambda c="gray66": self.select_category(widget_under_mouse,c))
        right_menu.add_cascade(label="Change Category", menu=category_menu)
        right_menu.add_command(label="Edit Task", command=lambda: self.edit_task(widget_under_mouse))
        right_menu.add_command(label="Delete Task", command=lambda: self.delete_task(widget_under_mouse))

        right_menu.tk_popup(event.x_root, event.y_root)
        
    def select_category(self, task, color):
        task.config(bg=color)
        current_font = tkFont.Font(font=task.cget("font"))
        current_font.configure(overstrike=False)
        task.config(font=current_font)

    def select_complete(self, task, color):
        task.config(bg=color)
        current_font = tkFont.Font(font=task.cget("font"))
        current_font.configure(overstrike=True)
        task.config(font=current_font)
    
    def edit_task(self, task):
        pre_text = task.cget("text")
        task_name = simpledialog.askstring("Edit Task", "Enter task name:", initialvalue=pre_text)
        if task_name:
            task.config(text=task_name)
        task_height = int(len(task_name))
        font_size = int(task_height/11)
        task.configure(font=("Arial", 12 - font_size), wraplength=100)

    def delete_task(self, task):
        task.destroy()

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


        self.selected_widget.place(x=x-window_x-self.offset_x-50, y=y-window_y-self.offset_y-25)

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
