from flask import Flask, render_template_string, request, redirect
from datetime import datetime
import threading
import time
import winsound
import os

app = Flask(__name__)


# FILES

SCHEDULE_FILE = "bell_schedule.txt"
HISTORY_FILE = "bell_history.txt"
SOUND_FILE = os.path.join("sounds", "school.wav")


# LOAD SCHEDULE

def load_schedule():
    if not os.path.exists(SCHEDULE_FILE):
        return ["07:30", "08:15", "09:00", "10:00", "06:14"]

    with open(SCHEDULE_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_schedule():
    with open(SCHEDULE_FILE, "w") as f:
        for t in bell_times:
            f.write(t + "\n")

def save_history(time_str):
    with open(HISTORY_FILE, "a") as f:
        f.write(time_str + "\n")

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return [line.strip() for line in f]

bell_times = load_schedule()
bell_history = load_history()


# RING BELL

def ring_bell():
    if os.path.exists(SOUND_FILE):
        for _ in range(3):
            winsound.PlaySound(SOUND_FILE, winsound.SND_FILENAME)
            time.sleep(1)
    else:
        print("Sound not found!")


# SCHEDULER

already_rung = set()

def bell_scheduler():
    global bell_history

    while True:
        current_time = datetime.now().strftime("%H:%M")

        if current_time in bell_times and current_time not in already_rung:
            ring_bell()
            already_rung.add(current_time)

            log = datetime.now().strftime("%H:%M:%S")
            bell_history.append(log)
            save_history(log)

        if current_time == "00:00":
            already_rung.clear()

        time.sleep(5)


# HTML UI

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Smart School Bell</title>

<style>

body{
    font-family:Arial, sans-serif;
    min-height: 100vh;
    position: relative;
    background:linear-gradient(135deg,#0f172a,#1e3a8a);
    padding:30px;
    color:white;
}
body::after {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;

    background: url("/static/bg.png") no-repeat center center/cover;
    opacity: 0.25;

    z-index: -1;
}
.container{
    max-width:900px;
    margin:auto;
}

.card{
    background:white;
    color:black;
    padding:20px;
    border-radius:15px;
    margin-bottom:20px;
}

h1{text-align:center;}

table{
    width:100%;
    border-collapse:collapse;
}

th{
    background:#2563eb;
    color:white;
    padding:10px;
}

td{
    text-align:center;
    padding:10px;
    border-bottom:1px solid #ddd;
}

.btn{
    background:#2563eb;
    color:white;
    padding:10px 20px;
    border:none;
    cursor:pointer;
    border-radius:10px;
}

.btn:hover{
    background:#1d4ed8;
}

#clock{
    font-size:40px;
    font-weight:bold;
    color:gold;
    text-align:center;
}

</style>
</head>

<body>
<div style="text-align:center; margin-bottom:20px;">
    <img src="/static/logo.png" width="120" style="border-radius:10px;">
</div>
<div class="container">

<h1>🔔 Smart School Bell System</h1>

<div id="clock"></div>

<div class="card">

<h2>📅 Bell Schedule</h2>

<table>
<tr>
<th>#</th>
<th>Time</th>
<th>Action</th>
</tr>

{% for t in bell_times %}
<tr>
<td>{{ loop.index }}</td>
<td>{{ t }}</td>
<td><a href="/delete/{{ t }}"> Delete</a></td>
</tr>
{% endfor %}

</table>

</div>

<div class="card">

<h2>➕ Add New Time</h2>

<form method="POST" action="/add_time">
<input type="time" name="new_time" required>
<button class="btn" type="submit">Add</button>
</form>

</div>

<div class="card">

<h2>🔔 Manual Bell</h2>

<form action="/ring">
<button class="btn" type="submit">Ring Now</button>
</form>

</div>

<div class="card">

<h2>📜 Bell History</h2>

<ul>
{% for h in bell_history %}
<li>{{ h }}</li>
{% endfor %}
</ul>

</div>

</div>

<script>
function updateClock(){
    document.getElementById("clock").innerHTML =
    new Date().toLocaleTimeString();
}
setInterval(updateClock,1000);
updateClock();
</script>

</body>
</html>
"""


# ROUTES

@app.route("/")
def home():
    return render_template_string(
        HTML,
        bell_times=bell_times,
        bell_history=bell_history
    )

@app.route("/add_time", methods=["POST"])
def add_time():
    new_time = request.form["new_time"]

    if new_time not in bell_times:
        bell_times.append(new_time)
        bell_times.sort()
        save_schedule()

    return redirect("/")

@app.route("/delete/<time>")
def delete_time(time):
    if time in bell_times:
        bell_times.remove(time)
        save_schedule()

    return redirect("/")

@app.route("/ring")
def manual_ring():
    ring_bell()
    log = datetime.now().strftime("%H:%M:%S")
    bell_history.append(log)
    save_history(log)

    return redirect("/")


# START APP

if __name__ == "__main__":
    t = threading.Thread(target=bell_scheduler, daemon=True)
    t.start()

    app.run(host="0.0.0.0", port=5000, debug=True)