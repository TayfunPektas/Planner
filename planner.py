import tkinter as tk
from tkinter import simpledialog
from tkinter.ttk import *
import tkinter.font as tkFont
import datetime
import json
import os
from tkinter import messagebox
#Planner V0.1.8
class WeeklyPlanner(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set title of the tkinter window.
        self.title("Chronivo")
        self.configure(background="white")
        self.task_id = 1  # To keep track of task IDs
        self.row_id = 1
        self.grid_widgets = {}  # To store widgets in the grid
        self.selected_widget = None
        self.offset_x = 0  # X offset for dragging
        self.offset_y = 0  # Y offset for dragging

        # Define Columns
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', "Parking Lot"]
        # Define Rows
        self.time_slots = [f"{i}:00" for i in range(8, 16)]

        self.create_grid()
        self.create_task_management()
        self.initial_load()

    def create_grid(self):
        self.canvases = []  # Store canvases for each column
        self.scrollbars = []  # Store scrollbars for future use

        # Create headers for days
        for col, day in enumerate(self.days):
            label = tk.Label(self, text=day, borderwidth=0, relief="solid", padx=10, pady=10, bg="white")
            label.grid(row=0, column=col, sticky="nsew")
            self.line_style = Style()
            self.line_style.configure("Line.TSeparator", background="#ed3c16")
            if not col == 7:
                separator_v = Separator(self, orient="vertical", style='Line.TSeparator')
                separator_v.grid(row=0, column=col, rowspan=1, columnspan=2, sticky="ns")
            else:
                pass
            

            # Create a canvas for each column
            canvas = tk.Canvas(self, width=100, height=300, highlightthickness=0, highlightbackground="red")
            canvas.grid(row=1, column=col, rowspan=len(self.time_slots), sticky="nsew")

            # Add a vertical scrollbar for each column (Initially hidden)
            scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
            scrollbar.place_forget()

            # Configure the canvas to work with the scrollbar
            canvas.configure(yscrollcommand=scrollbar.set)

            # Create a frame inside the canvas to hold the cells
            content_frame = tk.Frame(canvas, bg="white")
            canvas.create_window((0, 0), window=content_frame, anchor="nw")

            self.plus_label_top = tk.Label(self, text="+1", font=("Times New Roman", 8), bg="gray95")
            self.plus_label_bottom = tk.Label(self, text="+1", font=("Times New Roman", 8), bg="gray95")
            self.plus_label_top.lift()
            self.plus_label_bottom.lift()

            # Bind the frame to resize the canvas scroll region
            content_frame.bind("<Configure>", lambda e, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))

            # Save the canvas and scrollbar to lists for future reference
            self.canvases.append(canvas)
            self.scrollbars.append(scrollbar)

            # Bind mouse enter/leave events to show/hide scrollbars
            canvas.bind("<Enter>", lambda event, sb=scrollbar, cnv=canvas: self.show_scrollbar(sb, cnv))
            canvas.bind("<Leave>", lambda event, sb=scrollbar: self.hide_scrollbar(sb))

            # Bind mouse wheel scrolling to the canvas
            canvas.bind("<Enter>", lambda event, cnv=canvas: self.bind_mousewheel(cnv))
            canvas.bind("<Leave>", lambda event: self.unbind_mousewheel())

            # Create grid cells in the content frame
            for row in range(1, len(self.time_slots) + 1):
                frame = tk.Frame(content_frame, borderwidth=0, relief="solid", width=100, height=50, bg="white")
                frame.grid(row=row, column=0, sticky="nsew")

                # Bind mouse events for hover effects (optional)
                frame.bind("<Enter>", lambda e, f=frame: self.on_enter(f,canvas, scrollbar))
                frame.bind("<Leave>", lambda e, f=frame: self.on_leave(f))

                # Store the grid widget reference
                self.grid_widgets[(row, col)] = frame
                if col < len(self.days)-1:
                    separator_v = Separator(self, orient="vertical", style='Line.TSeparator')
                    separator_v.grid(row=row, column=col, rowspan=1, columnspan=2, sticky="ns")
        


    def show_scrollbar(self, scrollbar, canvas):
        # Show the scrollbar in the north-east corner of the canvas (relative to the canvas)
        #scrollbar.place(in_=canvas, relx=1.0, rely=0.0, relheight=1.0, anchor="ne")
        pass
    def hide_scrollbar(self, scrollbar):    
        # Hide the scrollbar
        scrollbar.place_forget()

    def bind_mousewheel(self, canvas):
        # Bind mouse wheel scrolling to the canvas
        canvas.bind_all("<MouseWheel>", lambda event: self._on_mousewheel(event, canvas))

    def unbind_mousewheel(self):
        # Unbind mouse wheel scrolling
        self.unbind_all("<MouseWheel>")

    def adding_one_labels(self, canvas):
        current_scroll = canvas.yview()
        # Unpack the scroll range
        top_position, bottom_position = current_scroll
        for widget in self.winfo_children():
            if widget.widgetName == "canvas":
                if not str(widget) == str(canvas):
                    for label_widget in widget.winfo_children():
                        label_widget.place_forget()
        self.canvas_value = (str(canvas)).replace(".!canvas", "")
        if self.canvas_value == "":
            self.canvas_value = 1
        # Determine if the canvas is scrolled down or up
        if top_position > 0.0:  # Scrolled down
            # Show the +1 sign at the top
            self.plus_label_top.place(x=canvas.winfo_width()*int(self.canvas_value) - 40, y=35, anchor="ne")
            self.plus_label_top.tkraise()
        else:
            # Hide the +1 sign at the top if at the top of the scroll
            self.plus_label_top.place_forget()

        # Check if we're near the bottom of the scroll range
        if bottom_position < 1.0:  # Not yet at the bottom
            self.plus_label_bottom.place(x=(canvas.winfo_width())*int(self.canvas_value) - 40, y=canvas.winfo_height()+36, anchor="se")
            self.plus_label_bottom.tkraise()
        else:
            # Hide the +1 sign at the bottom when fully scrolled down
            self.plus_label_bottom.place_forget()

    def _on_mousewheel(self, event, canvas):
        # Scroll the canvas with the mouse wheel
        canvas.yview_scroll(int(-1 * (event.delta / 100)), "units")
        self.adding_one_labels(canvas)

    def _on_mousewheel_initial(self, event):
        widget_under_cursor = self.winfo_containing(self.winfo_pointerx(), self.winfo_pointery())
        top_canvas = self.get_top_canvas(widget_under_cursor.place_info()["in"])
        top_canvas.yview_scroll(int(-1 * (event.delta / 100)), "units")
        self.adding_one_labels(top_canvas)
        
    def on_leave(self,frame):
        self.plus_label.place_forget()

    def on_enter(self,frame, canvas, scrollbar):
        self.plus_label = tk.Label(frame, text="+", font=("Times New Roman", 24), bg="ghost white", fg="gray90")
        self.plus_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        self.plus_label.bind("<Button-1>", lambda e, f=frame: self.on_frame_click(f, canvas, scrollbar))
        counter_label_lift = 0
        for widget in self.winfo_children():
            if widget.widgetName == "label":
                if widget.cget("text") in self.days:
                    counter_label_lift += 1
                    if counter_label_lift < 9:
                        widget.tkraise()
        for widget in self.winfo_children():    
            if widget.widgetName == "ttk::separator" or widget.widgetName == "button" or widget.widgetName == "ttk::combobox":
                widget.tkraise()
        for widget in self.winfo_children():
            if widget.widgetName == "label":
                if widget.cget("text") == "+1":
                    widget.tkraise()
        
    

    def get_top_canvas(self, widget):
        """
        Traverse up the widget hierarchy to find the top canvas.
        """
        parent_name = widget.winfo_parent()  # Get the parent widget's name (as a string)
        parent_widget = widget.nametowidget(parent_name)  # Convert the name to a widget object

        # Traverse up the hierarchy until we find a canvas widget
        while parent_widget and not isinstance(parent_widget, tk.Canvas):
            parent_name = parent_widget.winfo_parent()  # Get the parent's name
            parent_widget = parent_widget.nametowidget(parent_name)  # Get the actual parent widget

        return parent_widget  # Return the topmost canvas widget

    def on_frame_click(self, frame, canvas, scrollbar):
        top_canvas = self.get_top_canvas(frame)
        task_name = simpledialog.askstring("New Task", "Enter task name:")
        if task_name:
            task = tk.Label(self, text=task_name, bg="LightGoldenrod1", padx=20, pady=10, wraplength=100, justify="left")
            task.place(in_=frame, relheight=1, relwidth=1)
            task.bind("<Button-1>", self.on_task_click)
            task.bind("<Button-3>", lambda event: self.on_right_click(event, task))
            task.bind("<B1-Motion>", self.on_task_drag)
            task.bind("<ButtonRelease-1>", self.on_task_release)
            task.bind("<MouseWheel>", lambda event: self._on_mousewheel(event, top_canvas))
            task.bind("<Enter>", lambda event, sb=scrollbar, cnv=canvas: self.show_scrollbar(sb, cnv))
            task.bind("<Leave>", lambda event, sb=scrollbar: self.hide_scrollbar(sb))
            self.task_id += 1
            # Font is configured according to how many letters are in the task name.
            task_height = int(len(task_name))
            font_size = int(task_height / 9)
            task.configure(font=("Times New Roman", 12 - font_size), wraplength=100)
            parent_name = frame.winfo_parent()
            parent_widget = frame.nametowidget(parent_name)
            if (str(parent_widget.winfo_children()[-1])).split(".")[-1] == (str(frame)).split(".")[-1]:
                self.add_new_row(parent_widget,((str(parent_widget.winfo_children()[-1])).split(".")[-1]).replace("!frame",""),(str(parent_widget.winfo_children()[-1])).split(".")[1][-1],canvas, scrollbar)
        self.save()  
         
    def add_new_row(self, frame, row, column, canvas, scrollbar):
        if column == "s":
            column = 1
        frame = tk.Frame(frame, borderwidth=0, relief="solid", width=100, height=50, bg="white")
        frame.grid(row=int(row)+1, column=0, sticky="nsew")
        self.grid_widgets[(int(row)+1,int(column)-1)] = frame
        self.canvases[int(column)-1].configure(scrollregion=self.canvases[int(column)-1].bbox("all"))
        frame.bind("<Enter>", lambda e, f=frame: self.on_enter(f, canvas,scrollbar))
        frame.bind("<Leave>", lambda e, f=frame: self.on_leave(f))
        return frame

    def create_task_management(self):
        global week_combobox
        global year_combobox
        # Add button for changing the week to go down.
        add_left_button = tk.Button(self, text="←", command=self.left_button)
        add_left_button.grid(row=len(self.time_slots) + 1, column=2, sticky="e")
        # Get Current year
        current_year = datetime.datetime.now().year
        # Get weeks in the year.
        total_weeks = datetime.date(current_year, 12, 28).isocalendar()[1]
        weeks = [f"Week {week}" for week in range(1, total_weeks + 1)]
        # Add combobox for selecting the weeks.
        week_combobox = Combobox(self, values=weeks, width=10,state="readonly", postcommand=self.on_selection)
        week_combobox.grid(row=len(self.time_slots) + 1, column=3, columnspan=1)
        # Set current week of the year.
        week_combobox.set(f"Week {datetime.datetime.now().isocalendar()[1]}") 
        # Set what happens when week is selected from the combobox.
        week_combobox.bind("<<ComboboxSelected>>", self.on_week_combobox)
        # Add button for changing the week to go up.
        add_right_button = tk.Button(self, text="→", command=self.right_button)
        add_right_button.grid(row=len(self.time_slots) + 1, column=4, sticky="w")
        # Add combobox for selecting years.
        year_combobox = Combobox(self, values=["2024","2025","2026"], width=10,state="readonly", postcommand=self.on_selection)
        # Set current year.
        year_combobox.set(datetime.datetime.now().year)
        year_combobox.grid(row=len(self.time_slots) + 1, column=5)
        # Set what happens when year is selected from the combobox.
        year_combobox.bind("<<ComboboxSelected>>", self.on_year_combobox)

    def delete_tasks(self):
        # Delete all tasks from the current window.
        counter = 0
        for widget in self.winfo_children():
            if widget.widgetName == "label":
                counter += 1
                if not widget.cget("text") in self.days and not widget.cget("text") == "+1":
                    widget.destroy()
    
    def delete_all_tasks(self):
        response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete all tasks?")
        if response:
            counter = 0
            for widget in self.winfo_children():
                if widget.widgetName == "label":
                    counter += 1
                    if not widget.cget("text") in self.days and not widget.cget("text") == "+1":
                        widget.destroy()
        else:
            pass

    def on_selection(self):
        # Save current tasks.
        self.save()

    def on_week_combobox(self, event):
        # Set new week.
        self.delete_tasks()
        current_week = int(week_combobox.get().split(" ")[-1])
        current_year = int(year_combobox.get().split(" ")[-1])
        self.set_labels(current_week, current_year)
        for widget in self.winfo_children():
            if widget.widgetName == "canvas":
                widget.yview_moveto(0)


    def on_year_combobox(self, event):
        # Set new year.
        self.delete_tasks()
        current_year = int(year_combobox.get().split(" ")[-1])
        current_week = int(week_combobox.get().split(" ")[-1])
        self.set_labels(current_week, current_year)
        for widget in self.winfo_children():
            if widget.widgetName == "canvas":
                widget.yview_moveto(0)
        
    def delete_frames(self):
        for widget in self.winfo_children():
            widget.destroy()

    def set_labels(self, week, year):
        
        # If selected week and year exists in the folder load all the tasks to grids.
        if os.path.exists("database\\{}-{}.txt".format(f"Week {week}", year)):
            with open("database\\{}-{}.txt".format(f"Week {week}", year)) as load_file:
                date_array = json.load(load_file)
            self.delete_frames()
            self.create_grid()
            self.create_task_management()
            que_counter = -1
            for label in date_array:
                que_counter += 1
                date_label = tk.Label(self, text=label[0], bg=label[2], padx=20, pady=10, wraplength=100, justify="center")
                row = 0
                row = int(label[1].split("-")[-1])
                column = int(label[1].split("-")[0])
                canvas_counter = 0
                for widget in self.winfo_children():
                    if widget.widgetName == "canvas":
                        canvas_counter += 1
                        label_counter = 0
                        if canvas_counter == column:
                            for label_widget in widget.winfo_children()[-1].winfo_children():
                                frame_widget = widget.winfo_children()[-1]
                                label_counter += 1
                                if label_counter == row and not row > 8:  
                                    date_label.place(in_=label_widget, relheight=0.98, relwidth=0.99)
                                if row - label_counter == 1 and row > 8:
                                    scroll_counter = 0
                                    for scrollwidget in self.winfo_children():
                                        if scrollwidget.widgetName == "scrollbar":
                                            scroll_counter += 1
                                            if scroll_counter == column:
                                                scroll_widget = scrollwidget
                                                returned_frame = self.add_new_row(frame_widget,row-1,column,widget,scroll_widget)
                                                date_label.place(in_=returned_frame, relheight=0.98, relwidth=0.99)
                task_height = int(len(label[0]))
                font_size = int(task_height/9)
                date_label.configure(font=("Times New Roman", 12 - font_size), wraplength=100)
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
                date_label.bind("<MouseWheel>", lambda event: self._on_mousewheel_initial(event))
        else:
            pass
        last_frame_array = []
        last_row_array = []
        canvas_numbers = []
        canvas_count = 0
        for widget in self.winfo_children():
            if widget.widgetName == "canvas":
                canvas_count += 1
                last_widget = widget.winfo_children()[-1].winfo_children()[-1]
                last_frame_array.append(last_widget)
                last_row_array.append(len(widget.winfo_children()[-1].winfo_children()))
                canvas_numbers.append(canvas_count)
        for widget in self.winfo_children():
            if widget.widgetName == "label":
                if not widget.cget("text") in self.days and not widget.cget("text") == "+1":
                    for last_frame in last_frame_array:
                        try:
                            if str(widget.place_info()["in"]) == str(last_frame):
                                top_canvas = self.get_top_canvas(widget.place_info()["in"])
                                scroll_counter = 0
                                for scrollwidget in self.winfo_children():
                                    if scrollwidget.widgetName == "scrollbar":
                                        scroll_counter += 1
                                        
                                        if scroll_counter == canvas_numbers[last_frame_array.index(last_frame)]:
                                            canvas_index = 0
                                            for canvas in self.winfo_children():
                                                if canvas.widgetName == "canvas":
                                                    canvas_index += 1
                                                    if canvas == top_canvas:
                                                        column_number = canvas_index
                                            self.add_new_row(top_canvas.winfo_children()[-1], last_row_array[last_frame_array.index(last_frame)],column_number,top_canvas,scroll_widget)
                                            
                        except:
                            pass

    def left_button(self):
        # Command for week down button.
        for wigdet in self.winfo_children():
            if wigdet.widgetName == "label":
                if wigdet.cget("text") == "+1":
                    wigdet.place_forget()
        self.save()
        pre_week = int(week_combobox.get().split(" ")[-1]) - 1
        current_year = int(year_combobox.get().split(" ")[-1])
        self.set_labels(pre_week, current_year)
        week_combobox.set(f"Week {pre_week}")
        for widget in self.winfo_children():
            if widget.widgetName == "canvas":
                widget.yview_moveto(0)
        
    def right_button(self):
        # Command for week up button.
        for wigdet in self.winfo_children():
            if wigdet.widgetName == "label":
                if wigdet.cget("text") == "+1":
                    wigdet.place_forget()
        self.save()
        next_week = int(week_combobox.get().split(" ")[-1]) + 1
        current_year = int(year_combobox.get().split(" ")[-1])
        self.set_labels(next_week, current_year)
        week_combobox.set(f"Week {next_week}")
        for widget in self.winfo_children():
            if widget.widgetName == "canvas":
                widget.yview_moveto(0)
                
    def get_grid(self, frame_place_info):
        canvas = self.get_top_canvas(frame_place_info)
        column_info = 0
        column_counter = 0
        for widget in self.winfo_children():
            if widget.widgetName == "canvas":
                column_counter += 1
                if widget == canvas:
                    column_info = column_counter
        widget_counter = 0
        for widget in canvas.winfo_children()[-1].winfo_children():
            widget_counter += 1
            if widget == frame_place_info:
                row_info = widget_counter
                return column_info, row_info
    def save(self):
        # Save current tasks on the window.
        widgets_all = []
        counter_label = 0
        for widget in self.winfo_children():
            if widget.widgetName == "label":
                counter_label += 1
                if not widget.cget("text") in self.days and not widget.cget("text") == "+1":
                    label_widgets = []
                    label_widgets.append(widget.cget("text"))
                    grid_info = self.get_grid(widget.place_info()["in"])
                    label_widgets.append("{}-{}".format(grid_info[0], grid_info[1]))
                    label_widgets.append(widget.cget("bg"))
                    label_widgets.append(tkFont.Font(font=widget.cget("font")).cget("overstrike"))
                    widgets_all.append(label_widgets)
        widgets_all.sort(key=lambda x: (int(x[1].split("-")[0]), int(x[1].split("-")[1])))
        with open("database\\{}-{}.txt".format(week_combobox.get(), year_combobox.get()),"w") as save_file:
            json.dump(widgets_all, save_file)

    def initial_load(self):
        # Set tasks for initial tasks with current year and week.
        if os.path.exists("database\\{}-{}.txt".format(f"Week {datetime.datetime.now().isocalendar()[1]}", datetime.datetime.now().year)):
            with open("database\\{}-{}.txt".format(f"Week {datetime.datetime.now().isocalendar()[1]}", datetime.datetime.now().year)) as load_file:
                initial_array = json.load(load_file)
            que_counter = -1
            for label in initial_array:
                que_counter += 1
                initial_label = tk.Label(self, text=label[0], bg=label[2], padx=20, pady=10, wraplength=100, justify="center")
                row = 0
                row = int(label[1].split("-")[-1])
                column = int(label[1].split("-")[0])
                canvas_counter = 0
                for widget in self.winfo_children():
                    if widget.widgetName == "canvas":
                        canvas_counter += 1
                        label_counter = 0
                        if canvas_counter == column:
                            for label_widget in widget.winfo_children()[-1].winfo_children():
                                frame_widget = widget.winfo_children()[-1]
                                label_counter += 1
                                if label_counter == row and not row > 8:  
                                    initial_label.place(in_=label_widget, relheight=0.98, relwidth=0.99)
                                if row - label_counter == 1 and row > 8:
                                    scroll_counter = 0
                                    for scrollwidget in self.winfo_children():
                                        if scrollwidget.widgetName == "scrollbar":
                                            scroll_counter += 1
                                            if scroll_counter == column:
                                                scroll_widget = scrollwidget
                                                returned_frame = self.add_new_row(frame_widget,row-1,column,widget,scroll_widget)
                                                initial_label.place(in_=returned_frame, relheight=0.98, relwidth=0.99)

                task_height = int(len(label[0]))
                font_size = int(task_height/9)
                initial_label.configure(font=("Times New Roman", 12 - font_size), wraplength=100)
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
                initial_label.bind("<MouseWheel>", lambda event: self._on_mousewheel_initial(event))

        else:
            pass
        last_frame_array = []
        last_row_array = []
        canvas_numbers = []
        canvas_count = 0
        for widget in self.winfo_children():
            if widget.widgetName == "canvas":
                canvas_count += 1
                last_widget = widget.winfo_children()[-1].winfo_children()[-1]
                last_frame_array.append(last_widget)
                last_row_array.append(len(widget.winfo_children()[-1].winfo_children()))
                canvas_numbers.append(canvas_count)
        for widget in self.winfo_children():
            if widget.widgetName == "label":
                if not widget.cget("text") in self.days and not widget.cget("text") == "+1":
                    for last_frame in last_frame_array:
                        try:
                            if str(widget.place_info()["in"]) == str(last_frame):
                                top_canvas = self.get_top_canvas(widget.place_info()["in"])
                                scroll_counter = 0
                                for scrollwidget in self.winfo_children():
                                    if scrollwidget.widgetName == "scrollbar":
                                        scroll_counter += 1
                                        if scroll_counter == canvas_numbers[last_frame_array.index(last_frame)]:
                                            canvas_index = 0
                                            for canvas in self.winfo_children():
                                                if canvas.widgetName == "canvas":
                                                    canvas_index += 1
                                                    if canvas == top_canvas:
                                                        column_number = canvas_index
                                            self.add_new_row(top_canvas.winfo_children()[-1], last_row_array[last_frame_array.index(last_frame)],column_number,top_canvas,scroll_widget)
                        except:
                            pass

                            
                      

    def on_right_click(self,event, task):
        # Set right click menu
        widget_under_mouse = self.winfo_containing(event.x_root, event.y_root)
        right_menu = tk.Menu(self, tearoff=0)
        category_menu = tk.Menu(right_menu, tearoff=0)
        right_menu.add_command(label="Set as Complete", command=lambda c="lightgray": self.select_complete(widget_under_mouse,c))
        right_menu.add_command(label="Set as Ongoing", command=lambda c="LightGoldenrod1": self.select_category(widget_under_mouse,c))
        category_menu.add_command(label="Urgent", command=lambda c="brown1": self.select_category(widget_under_mouse,c))
        category_menu.add_command(label="High", command=lambda c="coral": self.select_category(widget_under_mouse,c))
        category_menu.add_command(label="Normal", command=lambda c="medium aquamarine": self.select_category(widget_under_mouse,c))
        category_menu.add_command(label="Low", command=lambda c="SlateGray2": self.select_category(widget_under_mouse,c))
        right_menu.add_cascade(label="Change Category", menu=category_menu)
        right_menu.add_command(label="Edit Task", command=lambda: self.edit_task(widget_under_mouse))
        right_menu.add_command(label="Delete Task", command=lambda: self.delete_task(widget_under_mouse))
        right_menu.add_command(label="Delete All Tasks", command=self.delete_all_tasks)
        right_menu.tk_popup(event.x_root, event.y_root)
        
    def select_category(self, task, color):
        # Set task category as "urgent" or "low" etc.
        task.config(bg=color)
        current_font = tkFont.Font(font=task.cget("font"))
        current_font.configure(overstrike=False)
        task.config(font=current_font)
        self.save()

    def select_complete(self, task, color):
        # Set task as complete.
        task.config(bg=color)
        current_font = tkFont.Font(font=task.cget("font"))
        current_font.configure(overstrike=True)
        task.config(font=current_font)
        self.save()
    
    def edit_task(self, task):
        # Set edit task and get current task name.
        pre_text = task.cget("text")
        task_name = simpledialog.askstring("Edit Task", "Enter task name:", initialvalue=pre_text)
        if task_name:
            task.config(text=task_name)
        task_height = int(len(task_name))
        font_size = int(task_height/9)
        task.configure(font=("Times New Roman", 12 - font_size), wraplength=100)
        self.save()

    def delete_task(self, task):
        # Delete selected task.
        task.destroy()
        self.save()

    def on_task_click(self, event):
        # Store the clicked widget and calculate the offset
        self.selected_widget = event.widget
        self.offset_x = self.selected_widget.winfo_x()
        self.offset_y = self.selected_widget.winfo_y()
        self.selected_widget.lift()
        
    def on_task_drag(self, event):
        # Move the widget with the mouse, taking the offset into account
        x= self.winfo_pointerx()
        y= self.winfo_pointery()
        window_x, window_y = self.winfo_rootx(), self.winfo_rooty()
        # -50 for x and -25 for y is used to center task after lifting.
        self.selected_widget.place(x=x-window_x-self.offset_x-50, y=y-window_y-self.offset_y-25)

    def on_task_release(self, event):
        # Snap the widget to the closest grid cell
        closest_frame = self.get_closest_frame(event.x_root, event.y_root)
        if closest_frame:
            self.selected_widget = event.widget
            frame = self.selected_widget.place_info()["in"]
            for widget in self.winfo_children():
                if widget.widgetName == "label":
                    if not widget.cget("text") in self.days and not widget.cget("text") == "+1":
                        try:
                            frame_grid_info = widget.place_info()["in"]
                        except:
                            frame_grid_info = frame
                        if frame_grid_info == closest_frame:
                            self.selected_widget.place_forget()
                            self.selected_widget.place(in_=frame, relwidth=0.99, relheight=0.97)
                            self.selected_widget = None
                            self.save()
                            break
            self.selected_widget.place_forget()  # Remove from the previous location
            self.selected_widget.place(in_=closest_frame, relwidth=0.99, relheight=0.97)  # Place in the new frame
        self.selected_widget = None
        self.save()

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

if __name__ == "__main__":
    app = WeeklyPlanner()
    app.mainloop()