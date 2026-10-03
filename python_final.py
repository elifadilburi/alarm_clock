import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import timedelta, datetime, timezone
import time
import os
import subprocess
import platform
import functions as time_tools


class ClockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("clock & timer app")
        self.geometry("900x650")

        self.dark_mode = False
        self.colors = {
            'light': {'bg': '#f0f0f0', 'fg': '#000000', 'comp_bg': '#ffffff', 'select': '#0078d7', 'map_bg': '#aaddff'},
            'dark': {'bg': "#2d2d2d", 'fg': '#ffffff', 'comp_bg': '#3d3d3d', 'select': '#555555', 'map_bg': '#1e3f5a'}
        }

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.clock = time_tools.AlarmClock()
        self.stopwatch = time_tools.Stopwatch()
        self.timer = None
        self.timer_active = False
        self.alarm_sounds = {}

        self.map_image = None
        self.current_selected_sound_display = tk.StringVar(value="none (silent)")
        self.current_sound_path_temp = None
        self.current_playback = None

        self.nav_btn1 = None
        self.nav_btn2 = None
        self.nav_btn3 = None
        self.nav_btn4 = None
        self.nav_btn5 = None
        self.theme_toggle = None
        self.notebook = None

        self.tab_alarm = None
        self.tab_stopwatch = None
        self.tab_timer = None
        self.tab_world_map = None
        self.tab_general_time = None

        self.alarm_hour = None
        self.alarm_minute = None
        self.alarm_label_entry = None
        self.alarm_repeat_var = None
        self.sound_label = None
        self.alarm_listbox = None
        self.stopwatch_label = None
        self.timer_label = None
        self.timer_entry = None
        self.world_map_canvas = None
        self.world_time_label = None
        self.country_combo = None
        self.general_time_label = None

        self.setup_ui()
        self.apply_theme()
        self.update_display_labels()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        header_frame = ttk.Frame(self, style='Header.TFrame')
        header_frame.pack(side='top', fill='x', pady=(0, 10))

        nav_container = ttk.Frame(header_frame, style='Header.TFrame')
        nav_container.pack(side='top', anchor='center', pady=10)

        self.nav_btn1 = ttk.Button(nav_container, text='alarm clock', command=lambda: self.notebook.select(0))
        self.nav_btn1.pack(side='left', padx=2)
        self.nav_btn2 = ttk.Button(nav_container, text='stopwatch', command=lambda: self.notebook.select(1))
        self.nav_btn2.pack(side='left', padx=2)
        self.nav_btn3 = ttk.Button(nav_container, text='timer', command=lambda: self.notebook.select(2))
        self.nav_btn3.pack(side='left', padx=2)
        self.nav_btn4 = ttk.Button(nav_container, text='world map', command=lambda: self.notebook.select(3))
        self.nav_btn4.pack(side='left', padx=2)
        self.nav_btn5 = ttk.Button(nav_container, text='general time', command=lambda: self.notebook.select(4))
        self.nav_btn5.pack(side='left', padx=2)

        theme_switch_frame = ttk.Frame(header_frame, style='Header.TFrame')
        theme_switch_frame.place(relx=1.0, rely=0.5, anchor='e', x=-20)

        ttk.Label(theme_switch_frame, text="dark mode", style='Header.TLabel').pack(side='left', padx=5)
        self.theme_toggle = ttk.Checkbutton(theme_switch_frame, command=self.toggle_theme, style='Switch.TCheckbutton')
        self.theme_toggle.pack(side='left')

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        self.tab_alarm = ttk.Frame(self.notebook, padding=10)
        self.tab_stopwatch = ttk.Frame(self.notebook, padding=10)
        self.tab_timer = ttk.Frame(self.notebook, padding=10)
        self.tab_world_map = ttk.Frame(self.notebook, padding=10)
        self.tab_general_time = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_alarm, text='alarm clock')
        self.notebook.add(self.tab_stopwatch, text='stopwatch')
        self.notebook.add(self.tab_timer, text='timer')
        self.notebook.add(self.tab_world_map, text='world map')
        self.notebook.add(self.tab_general_time, text='general time')

        self.style.layout('TNotebook.Tab', [])

        self.create_alarm_tab()
        self.create_stopwatch_tab()
        self.create_timer_tab()
        self.create_world_map_tab()
        self.create_general_time_tab()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        mode = 'dark' if self.dark_mode else 'light'
        c = self.colors[mode]
        self.configure(bg=c['bg'])
        self.style.configure('.', background=c['bg'], foreground=c['fg'], fieldbackground=c['comp_bg'])
        self.style.configure('TNotebook', background=c['bg'])
        self.style.configure('TFrame', background=c['bg'])
        self.style.configure('TLabel', background=c['bg'], foreground=c['fg'])
        self.style.configure('TButton', background=c['comp_bg'], foreground=c['fg'], borderwidth=1)
        self.style.map('TButton', background=[('active', c['select'])], foreground=[('active', c['fg'])])
        self.style.configure('TEntry', fieldbackground=c['comp_bg'], foreground=c['fg'])
        self.style.configure('TCheckbutton', background=c['bg'], foreground=c['fg'])
        self.style.configure('TLabelframe', background=c['bg'], foreground=c['fg'])
        self.style.configure('TLabelframe.Label', background=c['bg'], foreground=c['fg'])
        self.style.configure('Header.TFrame', background=c['comp_bg'])
        self.style.configure('Header.TLabel', background=c['comp_bg'], foreground=c['fg'])
        self.alarm_listbox.configure(bg=c['comp_bg'], fg=c['fg'], selectbackground=c['select'],
                                     selectforeground=c['fg'])
        if self.world_map_canvas:
            self.world_map_canvas.configure(bg=c['map_bg'])
        if self.stopwatch_label: self.stopwatch_label.configure(foreground=c['fg'])
        if self.timer_label: self.timer_label.configure(foreground=c['fg'])
        if self.world_time_label: self.world_time_label.configure(foreground=c['fg'])
        if self.general_time_label: self.general_time_label.configure(foreground=c['fg'])

    def create_alarm_tab(self):
        add_frame = ttk.LabelFrame(self.tab_alarm, text="set new alarm")
        add_frame.pack(fill='x', pady=10)

        ttk.Label(add_frame, text="time:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        time_input_frame = ttk.Frame(add_frame)
        time_input_frame.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        self.alarm_hour = tk.Spinbox(time_input_frame, from_=0, to=23, width=3, format="%02.0f", state='readonly', wrap=True)
        self.alarm_hour.pack(side='left')

        ttk.Label(time_input_frame, text=":").pack(side='left')

        self.alarm_minute = tk.Spinbox(time_input_frame, from_=0, to=59, width=3, format="%02.0f", state='readonly', wrap=True)
        self.alarm_minute.pack(side='left')

        self.alarm_repeat_var = tk.BooleanVar()
        ttk.Checkbutton(add_frame, text="repeat", variable=self.alarm_repeat_var).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(add_frame, text="label:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.alarm_label_entry = ttk.Entry(add_frame, width=20)
        self.alarm_label_entry.grid(row=1, column=1, padx=5, pady=5, columnspan=2)

        ttk.Label(add_frame, text="ringtone:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        sound_frame = ttk.Frame(add_frame)
        sound_frame.grid(row=2, column=1, columnspan=2, sticky='w')

        self.sound_label = ttk.Label(sound_frame, textvariable=self.current_selected_sound_display, width=15)
        self.sound_label.pack(side='left', padx=5)
        ttk.Button(sound_frame, text="browse...", command=self.browse_ringtone, width=8).pack(side='left')

        ttk.Button(add_frame, text="add alarm", command=self.gui_add_alarm).grid(row=3, column=1, padx=5, pady=10)

        list_frame = ttk.LabelFrame(self.tab_alarm, text="active alarms")
        list_frame.pack(fill='both', expand=True)
        self.alarm_listbox = tk.Listbox(list_frame)
        self.alarm_listbox.pack(fill='both', expand=True, side='left', padx=(5, 0), pady=5)
        list_controls = ttk.Frame(list_frame)
        list_controls.pack(side='right', fill='y', padx=5)
        ttk.Button(list_controls, text="remove", command=self.gui_remove_alarm).pack(pady=5)
        ttk.Button(list_controls, text="refresh", command=self.gui_update_alarm_list).pack(pady=5)
        self.gui_update_alarm_list()

    def browse_ringtone(self):
        filename = filedialog.askopenfilename(title="select ringtone",
                                              filetypes=(("wav files", "*.wav"), ("mp3 files", "*.mp3"), ("all files", "*.*")))
        if filename:
            abs_path = os.path.abspath(filename)
            self.current_sound_path_temp = abs_path
            display_name = os.path.basename(abs_path)
            if len(display_name) > 15: display_name = display_name[:12] + "..."
            self.current_selected_sound_display.set(display_name)

    def create_stopwatch_tab(self):
        self.tab_stopwatch.rowconfigure(0, weight=1)
        self.tab_stopwatch.columnconfigure(0, weight=1)
        display_frame = ttk.Frame(self.tab_stopwatch)
        display_frame.grid(row=0, column=0)
        self.stopwatch_label = ttk.Label(display_frame, text="00:00:00.000", font=("Helvetica", 36))
        self.stopwatch_label.pack(pady=20)
        controls_frame = ttk.Frame(display_frame)
        controls_frame.pack(pady=10)
        ttk.Button(controls_frame, text="start", command=self.stopwatch.start).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="stop", command=self.stopwatch.stop).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="reset", command=self.gui_stopwatch_reset).pack(side='left', padx=5)

    def create_timer_tab(self):
        self.tab_timer.rowconfigure(0, weight=1)
        self.tab_timer.columnconfigure(0, weight=1)
        display_frame = ttk.Frame(self.tab_timer)
        display_frame.grid(row=0, column=0)
        self.timer_label = ttk.Label(display_frame, text="00:00:00", font=("Helvetica", 36))
        self.timer_label.pack(pady=20)
        set_frame = ttk.Frame(display_frame)
        set_frame.pack(pady=5)
        ttk.Label(set_frame, text="set duration (sec):").pack(side='left', padx=5)
        self.timer_entry = ttk.Entry(set_frame, width=10)
        self.timer_entry.pack(side='left')
        controls_frame = ttk.Frame(display_frame)
        controls_frame.pack(pady=10)
        ttk.Button(controls_frame, text="start", command=self.gui_timer_start).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="cancel", command=self.gui_timer_cancel).pack(side='left', padx=5)

    def create_world_map_tab(self):
        map_container = ttk.Frame(self.tab_world_map)
        map_container.pack(fill='both', expand=True, padx=20, pady=20)
        top_bar = ttk.Frame(map_container)
        top_bar.pack(fill='x', pady=(0, 10))
        ttk.Label(top_bar, text="click on the map to see local time", font=("Helvetica", 12)).pack(side='left')

        self.world_map_canvas = tk.Canvas(map_container, bg='#aaddff', height=400, width=800)
        self.world_map_canvas.pack(expand=True)

        self.load_map_image("world_map (1).png")
        self.world_map_canvas.bind("<Button-1>", self.on_map_click)
        self.world_time_label = ttk.Label(map_container, text="select a location...", font=("Helvetica", 20, "bold"))
        self.world_time_label.pack(pady=20)
        

    def create_general_time_tab(self):
        container = ttk.Frame(self.tab_general_time)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        ttk.Label(container, text="select a country/region:", font=("Helvetica", 12)).pack(pady=(0, 10))
        self.time_offsets = {
            "argentina": -3, "australia (sydney)": 11, "brazil (sao paulo)": -3,
            "canada (toronto)": -5, "canada (vancouver)": -8, "china": 8,
            "egypt": 2, "france": 1, "germany": 1, "india": 5.5, "italy": 1,
            "japan": 9, "mexico (city)": -6, "new zealand": 12, "russia (moscow)": 3, "romania":2, 
            "singapore": 8, "south africa": 2, "south korea": 9, "spain": 1,
            "turkey": 3, "uae (dubai)": 4, "united kingdom": 0,
            "usa (california)": -8, "usa (new york)": -5, "usa (texas)": -6
        }
        country_names = sorted(list(self.time_offsets.keys()))
        self.country_combo = ttk.Combobox(container, values=country_names, state="readonly", width=30)
        self.country_combo.pack(pady=10)
        self.country_combo.bind("<<ComboboxSelected>>", self.update_general_time)
        self.general_time_label = ttk.Label(container, text="--:--:--", font=("Helvetica", 36))
        self.general_time_label.pack(pady=30)

    def update_general_time(self, event=None):
        selection = self.country_combo.get()
        if selection in self.time_offsets:
            offset = self.time_offsets[selection]
            utc_now = datetime.now(timezone.utc)
            target_time = utc_now + timedelta(hours=offset)
            time_str = target_time.strftime("%H:%M:%S")
            date_str = target_time.strftime("%A, %d %B")
            self.general_time_label.config(text=f"{time_str}\n{date_str}")
            self.after(1000, lambda: self.update_general_time() if self.country_combo.get() == selection else None)

    def load_map_image(self, path):
        try:
            if os.path.isabs(path):
                image_path = path
            else:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                image_path = os.path.join(script_dir, path)
            self.map_image = tk.PhotoImage(file=image_path)
            self.world_map_canvas.delete("all")
            self.world_map_canvas.create_image(0, 0, image=self.map_image, anchor='nw')
            self.world_map_canvas.config(width=self.map_image.width(), height=self.map_image.height())
        except (tk.TclError, FileNotFoundError):
            self.world_map_canvas.delete("all")
            self.world_map_canvas.create_text(400, 200, text="no map image loaded.",
                                              justify='center')

    def on_map_click(self, event):
        width = self.map_image.width() if self.map_image else self.world_map_canvas.winfo_width()
        center_x = (width / 2.3)
        pixels_per_hour = width / 24
        offset_hours = (event.x - center_x) / pixels_per_hour
        offset_int = round(offset_hours)
        if offset_int > 12: offset_int = 12
        if offset_int < -12: offset_int = -12
        utc_now = datetime.now(timezone.utc)
        target_time = utc_now + timedelta(hours=offset_int)
        sign = "+" if offset_int >= 0 else ""
        tz_str = f"utc{sign}{offset_int}"
        time_str = target_time.strftime("%H:%M:%S")
        date_str = target_time.strftime("%A, %d %B")
        self.world_time_label.config(text=f"{time_str}\n{date_str} ({tz_str})")
        self.world_map_canvas.delete("click_marker")
        r = 6
        self.world_map_canvas.create_oval(event.x - r, event.y - r, event.x + r, event.y + r, fill='red',
                                          outline='white', width=2, tags="click_marker")

    def gui_add_alarm(self):
        time_str = f"{self.alarm_hour.get()}:{self.alarm_minute.get()}"
        label = self.alarm_label_entry.get()
        repeat = self.alarm_repeat_var.get()
        
        if not label:
            messagebox.showwarning("input error", "provide a label")
            return

        if self.current_sound_path_temp:
            self.alarm_sounds[label] = self.current_sound_path_temp

        self.clock.add_alarm(time_str, label, repeat, ring_callback=self.gui_alarm_popup)
        self.gui_update_alarm_list()

        self.alarm_label_entry.delete(0, tk.END)
        self.alarm_repeat_var.set(False)
        self.current_selected_sound_display.set("none (silent)")
        self.current_sound_path_temp = None

    def gui_remove_alarm(self):
        try:
            selected_index = self.alarm_listbox.curselection()[0]
            all_alarms = self.clock.list_alarms()
            target_alarm = all_alarms[selected_index]
            label = target_alarm['label']

            self.clock.remove_alarm(label)
            if label in self.alarm_sounds:
                del self.alarm_sounds[label]
            self.gui_update_alarm_list()
        except IndexError:
            messagebox.showwarning("selection error", "select an alarm to remove.")

    def gui_update_alarm_list(self):
        self.alarm_listbox.delete(0, tk.END)
        alarms = self.clock.list_alarms()
        for alarm in alarms:
            status = "active" if alarm['active'] else "inactive"
            label = alarm['label']

            sound_path = self.alarm_sounds.get(label)
            if sound_path:
                sound_name = os.path.basename(sound_path)
            else:
                sound_name = "silent"

            self.alarm_listbox.insert(tk.END, f"{alarm['time']} - {label} - {sound_name} ({status})")

    def gui_alarm_popup(self, message):
        sound_file = self.alarm_sounds.get(message)

        if sound_file and os.path.exists(sound_file):
            try:
                if platform.system() == "Darwin":
                    self.current_playback = subprocess.Popen(["afplay", sound_file])
            except Exception:
                pass
        self.after(0, self.show_alarm_popup, message)

    def show_alarm_popup(self, message):
        messagebox.showinfo("alarm!", message)
        if self.current_playback:
             self.current_playback.terminate()
             self.current_playback = None
        self.gui_update_alarm_list()

    def gui_stopwatch_reset(self):
        self.stopwatch.reset()
        self.stopwatch_label.config(text="00:00:00.000")

    def gui_timer_start(self):
        try:
            duration = int(self.timer_entry.get())
            if duration <= 0: raise ValueError
            self.timer = time_tools.Timer(duration, time_up_callback=self.gui_timer_popup)
            self.timer.start()
            self.timer_active = True
        except ValueError:
            messagebox.showwarning("input error", "enter a valid number of seconds.")

    def gui_timer_cancel(self):
        if self.timer: self.timer.cancel()
        self.timer_active = False
        self.timer_label.config(text="00:00:00")

    def gui_timer_popup(self):
        self.after(0, self.show_timer_popup)

    def show_timer_popup(self):
        messagebox.showinfo("timer finished", "time's up!")
        self.timer_active = False
        self.timer_label.config(text="00:00:00")

    def update_display_labels(self):
        if self.stopwatch.running:
            elapsed = self.stopwatch.get_elapsed()
            hours, rem = divmod(elapsed, 3600)
            minutes, seconds = divmod(rem, 60)
            millis = int((seconds - int(seconds)) * 1000)
            self.stopwatch_label.config(text=f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{millis:003}")
        if self.timer_active and self.timer:
            remaining = self.timer.get_remaining()
            if remaining > 0:
                td = timedelta(seconds=int(remaining + 0.999))
                self.timer_label.config(text=str(td))
            else:
                self.timer_active = False
                self.timer_label.config(text="00:00:00")
        self.after(50, self.update_display_labels)

    def on_close(self):
        for alarm in self.clock.alarms: alarm.stop()
        if self.timer: self.timer.cancel()
        if self.current_playback:
             self.current_playback.terminate()
        self.destroy()


if __name__ == "__main__":
    app = ClockApp()
    app.mainloop()