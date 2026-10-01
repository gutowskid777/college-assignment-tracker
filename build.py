#!/usr/bin/env python3
"""Build index.html from index.src.html + a state JSON.

Usage:
  python3 build.py state.json            # state from a JSON file
  python3 build.py db-dump.json          # or a tracker/state dump from the artifact database ({"state": ...})
  python3 build.py artifact-dump.html    # or pull state out of an old saved artifact HTML

On claude.ai the live data is in the artifact database (doc tracker/state), not the
page. The embedded state is only the first paint; the page adopts the database copy
on load. Read the database before rebuilding so the embedded copy is current.
"""
import json, re, sys, time, pathlib

here = pathlib.Path(__file__).parent
src = (here / 'index.src.html').read_text()

arg = sys.argv[1] if len(sys.argv) > 1 else None
if not arg:
    sys.exit('usage: build.py <state.json | db-dump.json | saved-artifact.html>')
raw = pathlib.Path(arg).read_text()
if arg.endswith('.html'):
    m = re.search(r'<script type="application/json" id="db-state">(.*?)</script>', raw, re.S)
    state = json.loads(m.group(1))
else:
    state = json.loads(raw)
    if 'state' in state and 'semesters' not in state:
        state = state['state']

# Stamp the build so a stale device copy never outranks a freshly published one.
# Demo data (demoAnchor set) is left unstamped so any visitor's own edits win.
if 'demoAnchor' not in state:
    state['updatedAt'] = int(time.time() * 1000)
state_str = json.dumps(state, separators=(',', ':')).replace('</', '<\\/')
out = src.replace('__STATE__', state_str)
(here / 'index.html').write_text(out)
print(f'index.html built: {len(out)} bytes, '
      f'{sum(len(s["assignments"]) for s in state["semesters"])} assignments, '
      f'active={state["activeSemester"]}')
