python - <<'PY'
import sqlite3,json,pathlib,difflib
DB=r'C:/Users/theai/AppData/Local/hermes/profiles/d-drive-profile/state.db'; con=sqlite3.connect(DB)
tc=json.loads(con.execute('select tool_calls from messages where id=4051').fetchone()[0])[0]
a=tc['function']['arguments']; a=json.loads(a) if isinstance(a,str) else a; src=a['content']
tc=json.loads(con.execute('select tool_calls from messages where id=4057').fetchone()[0])[0]
a=tc['function']['arguments']; a=json.loads(a) if isinstance(a,str) else a; rec=src.replace(a['old_string'],a['new_string'])
cur=pathlib.Path(r'D:/Projects/ToE_21st_June_NEWEST/historical_hermes_general_fts_state_recovered.py').read_text()
print(''.join(difflib.unified_diff(rec.splitlines(True),cur.splitlines(True),fromfile='db_reconstructed',tofile='current')))
PY
