import streamlit as st
import time
import datetime
import pytz

# Set timezone
local_tz = pytz.timezone("Asia/Singapore")

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "bedtime_hour" not in st.session_state:
    st.session_state.bedtime_hour = 23

if "bedtime_minute" not in st.session_state:
    st.session_state.bedtime_minute = 0

st.title("🗓️ Task Tracker + Bedtime Monitor")

# --- Task Input ---
with st.form("add_task_form"):
    cols = st.columns([2, 1])
    task_name = cols[0].text_input("Task")
    task_duration = cols[1].number_input("Est. Duration (min)", min_value=1, max_value=600, value=30)
    submitted = st.form_submit_button("➕ Add Task")
    if submitted and task_name:
        st.session_state.tasks.append({
            "name": task_name,
            "estimated": task_duration,
            "start_time": None,
            "elapsed": 0,
            "actual": None
        })

# --- Bedtime Input ---
bh, bm = st.columns(2)
st.session_state.bedtime_hour = bh.number_input("Bedtime Hour", 0, 23, st.session_state.bedtime_hour)
st.session_state.bedtime_minute = bm.number_input("Minute", 0, 59, st.session_state.bedtime_minute)

st.divider()

# --- Task List ---
st.subheader("📝 Tasks")
task_container = st.container()
for i, task in enumerate(st.session_state.tasks):
    running = task["start_time"] is not None
    elapsed = task["elapsed"] + (time.time() - task["start_time"] if running else 0)
    actual_min = int(elapsed // 60)
    
    cols = st.columns([4, 1, 1, 1])
    cols[0].markdown(f"**{i+1}. {task['name']}** — Est: {task['estimated']} min | {'⏱️ Running' if running else 'Actual'}: {actual_min} min")
    
    if cols[1].button("Start", key=f"start_{i}"):
        if not running:
            task["start_time"] = time.time()
    if cols[2].button("Stop", key=f"stop_{i}"):
        if running:
            task["elapsed"] += time.time() - task["start_time"]
            task["start_time"] = None
            task["actual"] = int(task["elapsed"] // 60)
    if cols[3].button("🗑️", key=f"del_{i}"):
        st.session_state.tasks.pop(i)
        st.experimental_rerun()

st.divider()

# --- Summary ---
if st.button("📊 Show Summary"):
    now = datetime.datetime.now(local_tz)
    bedtime = now.replace(hour=st.session_state.bedtime_hour, minute=st.session_state.bedtime_minute, second=0, microsecond=0)
    if now > bedtime:
        bedtime += datetime.timedelta(days=1)
    
    time_left = int((bedtime - now).total_seconds() / 60)
    total_est = sum(t["estimated"] for t in st.session_state.tasks)
    total_actual = sum((t["elapsed"] + (time.time() - t["start_time"] if t["start_time"] else 0)) for t in st.session_state.tasks)
    total_actual_min = int(total_actual / 60)

    st.write("**🕒 Current Time:**", now.strftime("%H:%M"))
    st.write("**🛌 Bedtime:**", bedtime.strftime("%H:%M"))
    st.write(f"**⏳ Time Remaining:** {time_left} min")
    st.write(f"**📋 Estimated Task Total:** {total_est} min")
    st.write(f"**🕓 Actual Time Total:** {total_actual_min} min")

    if total_est > time_left:
        st.warning(f"⚠️ Overbooked (Est.): by {total_est - time_left} min")
    else:
        st.success(f"✅ Est OK: {time_left - total_est} min remaining")

    if total_actual_min > time_left:
        st.warning(f"⚠️ Overbooked (Actual): by {total_actual_min - time_left} min")
    else:
        st.info(f"🟢 Actual OK: {time_left - total_actual_min} min remaining")
