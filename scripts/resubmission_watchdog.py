"""Watchdog for an unattended resubmission run (generalised from the E7 watchdog).

Usage: python scripts/resubmission_watchdog.py <run.log> '<driver pgrep pattern>' '<step pgrep pattern>'

Every 60 s while the driver runs:
  - PAUSE (SIGSTOP the driver and step processes) if kernel memory pressure is critical (level 4);
  - PAUSE if, over the trailing 30 min, the run log has not grown AND the python steps used
    < 60 s of CPU. (Log silence alone is not enough, which is why the steps also run with
    ``python -u``: a stalled HF download lock caught E7 on 2026-09-29.)
Exits on its own when the driver is gone. Never pauses on swap.
Resume with the kill -CONT line it prints.
"""
import subprocess
import sys
import time
from pathlib import Path

RUNLOG = Path(sys.argv[1])
DRIVER_PAT = sys.argv[2]
STEP_PAT = sys.argv[3]
STALL = 30 * 60


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()


def note(msg):
    print(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] watchdog: {msg}", flush=True)


def pause(reason):
    pids = sh(f"pgrep -f '{DRIVER_PAT}|{STEP_PAT}'").split()
    for p in pids:
        subprocess.run(["kill", "-STOP", p])
    note(f"PAUSED ({reason}); SIGSTOP {' '.join(pids)}; resume with: kill -CONT {' '.join(pids)}")


def cpu_seconds(pids):
    total = 0.0
    for p in pids:
        t = sh(f"ps -o time= -p {p}")  # [[dd-]hh:]mm:ss.xx
        if not t:
            continue
        d, _, rest = t.rpartition("-")
        parts = [float(x) for x in rest.split(":")]
        secs = sum(v * 60 ** i for i, v in enumerate(reversed(parts)))
        total += secs + (int(d) * 86400 if d else 0)
    return total


note(f"started for {RUNLOG} (pause only on critical pressure, or 30 min with no log growth and < 60 s CPU)")
cpu_hist = []
while True:
    time.sleep(60)
    if not sh(f"pgrep -f '{DRIVER_PAT}'"):
        break
    if sh("sysctl -n kern.memorystatus_vm_pressure_level") == "4":
        pause("memory pressure critical")
        break
    py = sh(f"pgrep -f '{STEP_PAT}'").split()
    now = time.time()
    cpu_hist = [(t, c) for t, c in cpu_hist if now - t <= STALL + 90] + [(now, cpu_seconds(py))]
    if not py or now - cpu_hist[0][0] < STALL:
        continue
    cpu_used = cpu_hist[-1][1] - cpu_hist[0][1]
    log_age = now - RUNLOG.stat().st_mtime if RUNLOG.exists() else 0
    if log_age > STALL and cpu_used < 60:
        pause(f"no log progress for {int(log_age / 60)} min and only {cpu_used:.0f} s CPU in {int(STALL / 60)} min")
        break
note("exiting")
