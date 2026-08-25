#!/usr/bin/env python3
"""Build index.html from index.src.html + a state JSON.

Usage:
  python3 build.py state.json            # state from a JSON file
  python3 build.py artifact-dump.html    # or pull state out of a saved artifact HTML

The template embeds ITSELF base64-encoded (the #tpl tag) so the published page can
rebuild a clean document when it saves, instead of snapshotting the live DOM
(which would bake in claude.ai's injected frame runtime and corrupt the artifact).
"""
import base64, json, re, sys, pathlib

here = pathlib.Path(__file__).parent
src = (here / 'index.src.html').read_text()

arg = sys.argv[1] if len(sys.argv) > 1 else None
if not arg:
    sys.exit('usage: build.py <state.json | saved-artifact.html>')
raw = pathlib.Path(arg).read_text()
if arg.endswith('.html'):
    m = re.search(r'<script type="application/json" id="db-state">(.*?)</script>', raw, re.S)
    state = json.loads(m.group(1))
else:
    state = json.loads(raw)

state_str = json.dumps(state, separators=(',', ':')).replace('</', '<\\/')
tpl_b64 = base64.b64encode(src.encode('utf-8')).decode('ascii')
out = src.replace('__STATE__', state_str).replace('__TPL__', tpl_b64)
(here / 'index.html').write_text(out)
print(f'index.html built: {len(out)} bytes, '
      f'{sum(len(s["assignments"]) for s in state["semesters"])} assignments, '
      f'active={state["activeSemester"]}')
