import streamlit as st
st.title("Task Tracker")

import datetime
import pytz
import time
import ipywidgets as widgets
from IPython.display import display, clear_output
from functools import partial

# Timezone
local_tz = pytz.timezone("Asia/Singapore")
tasks = []

# Task input widgets
task_name_input = widgets.Text(description="Task")
task_duration_input = widgets.BoundedIntText(value=30, min=1, max=600, description="Est (min)")
add_button = widgets.Button(description="➕ Add Task", button_style="success")

# Bedtime input widgets
bedtime_hour_input = widgets.BoundedIntText(value=23, min=0, max=23, description="Bed Hr")
bedtime_minute_input = widgets.BoundedIntText(value=0, min=0, max=59, description="Min")

# Outputs
task_list_output = widgets.Output()
summary_output = widgets.Output()
logs_output = widgets.Output()

task_list_container = widgets.VBox()

# Add a task
def add_task(_):
    name = task_name_input.value.strip()
    duration = task_duration_input.value
    if not name:
        return
    task = {
        "name": name,
        "estimated": duration,
        "start_time": None,
        "end_time": None,
        "actual": None,
        "elapsed": 0
    }
    tasks.append(task)
    task_name_input.value = ""
    task_duration_input.value = 30
    render_task_list()

# Start task
def start_task(task, button):
    if task["start_time"] is None:
        task["start_time"] = time.time()
        with logs_output:
            print(f"▶️ Started: {task['name']}")

# Stop task
def stop_task(task, button):
    if task["start_time"] is None:
        with logs_output:
            print(f"⚠️ Not running: {task['name']}")
        return
    elapsed = time.time() - task["start_time"]
    task["elapsed"] += elapsed
    task["start_time"] = None
    task["actual"] = int(task["elapsed"] / 60)
    with logs_output:
        print(f"⏹️ Stopped: {task['name']} — Total: {task['actual']} min")
    render_task_list()

# Delete task
def delete_task(index, button):
    del tasks[index]
    with logs_output:
        print(f"🗑️ Deleted task #{index + 1}")
    render_task_list()

def render_task_list():
    rows = []
    for i, task in enumerate(tasks):
        est = task['estimated']
        if task["start_time"] is not None:
            running_time = (time.time() - task["start_time"]) + task["elapsed"]
            actual = int(running_time / 60)
            label = f"<b>{i+1}. {task['name']}</b> — Est: {est} min | ⏱️ Running: {actual} min"
        else:
            actual = int(task["elapsed"] / 60) if task["elapsed"] > 0 else "--"
            label = f"<b>{i+1}. {task['name']}</b> — Est: {est} min | Actual: {actual} min"

        task_label = widgets.HTML(label)
        start_btn = widgets.Button(description="Start", layout=widgets.Layout(width="60px"))
        stop_btn = widgets.Button(description="Stop", layout=widgets.Layout(width="60px"))
        delete_btn = widgets.Button(description="🗑️", layout=widgets.Layout(width="40px"))

        start_btn.on_click(partial(start_task, task))
        stop_btn.on_click(partial(stop_task, task))
        delete_btn.on_click(partial(delete_task, i))

        row = widgets.HBox([task_label, start_btn, stop_btn, delete_btn])
        rows.append(row)

    task_list_container.children = rows


# Refresh running task timers manually
refresh_button = widgets.Button(description="🔄 Refresh Timers", button_style="warning")
refresh_button.on_click(lambda _: render_task_list())

# Show bedtime summary
def show_summary(_):
    now = datetime.datetime.now(local_tz)
    bedtime = now.replace(hour=bedtime_hour_input.value,
                          minute=bedtime_minute_input.value,
                          second=0, microsecond=0)
    if now > bedtime:
        bedtime += datetime.timedelta(days=1)

    time_left = int((bedtime - now).total_seconds() / 60)
    total_est = sum(t['estimated'] for t in tasks)
    total_actual = sum(
        (t["elapsed"] + (time.time() - t["start_time"]) if t["start_time"] else t["elapsed"])
        for t in tasks
    )
    total_actual = int(total_actual / 60)

    with summary_output:
        clear_output()
        print("🕒 Current Time:", now.strftime("%H:%M"))
        print("🛌 Bedtime:", bedtime.strftime("%H:%M"))
        print(f"⏳ Time remaining: {time_left} min")
        print(f"📋 Estimated Task Total: {total_est} min")
        print(f"🕓 Actual Time Total: {total_actual} min")

        if total_est > time_left:
            print(f"⚠️ Overbooked (Est): by {total_est - time_left} min")
        else:
            print(f"✅ Est OK: {time_left - total_est} min remaining")
        if total_actual > time_left:
            print(f"⚠️ Overbooked (Actual): by {total_actual - time_left} min")
        else:
            print(f"🟢 Actual OK: {time_left - total_actual} min remaining")

# Summary button
summary_button = widgets.Button(description="📊 Show Summary", button_style="info")
summary_button.on_click(show_summary)

# Link Add Task
add_button.on_click(add_task)

# Display layout
display(widgets.VBox([
    widgets.HTML("<h3>🗓️ Task Tracker + Bedtime Monitor</h3>"),
    widgets.HBox([bedtime_hour_input, bedtime_minute_input]),
    task_name_input,
    task_duration_input,
    add_button,
    widgets.HTML("<hr><h4>📝 Tasks:</h4>"),
    task_list_container,  # <== updated here
    refresh_button,
    widgets.HTML("<hr>"),
    summary_button,
    summary_output,
    widgets.HTML("<hr><h4>🪵 Logs:</h4>"),
    logs_output
]))

