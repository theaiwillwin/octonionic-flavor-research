python -c 'from pathlib import Path
from datetime import datetime
roots=[Path("/d/Projects/ToE_21st_June_NEWEST"),Path("/c/Users/theai/AppData/Local/hermes/profiles/d-drive-profile/skills/software-development/verified-algebra-workflow"),Path("/c/Users/theai/AppData/Local/hermes/profiles/d-drive-profile/personal")]
for root in roots:
 print("ROOT",root)
 rows=[]
 for p in root.rglob("*"):
  if p.is_file():
   t=datetime.fromtimestamp(p.stat().st_mtime)
   if t.date().isoformat()>="2026-07-14": rows.append((t.isoformat(timespec="seconds"),str(p),p.stat().st_size))
 for row in sorted(rows,reverse=True): print("\t".join(map(str,row)))'
