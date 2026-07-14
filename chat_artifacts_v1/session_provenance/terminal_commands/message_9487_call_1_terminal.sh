python - <<'PY'
import sqlite3,json,hashlib,pathlib
DB=r'C:/Users/theai/AppData/Local/hermes/profiles/d-drive-profile/state.db'
con=sqlite3.connect(DB)
rows={i:con.execute('select content,tool_calls from messages where id=?',(i,)).fetchone() for i in (4051,4058,4060)}
tc=json.loads(rows[4051][1])
# tool_calls is list; arguments may be JSON text
call=tc[0]
args=call.get('function',call).get('arguments')
if isinstance(args,str): args=json.loads(args)
source=args['content']
patch_record=rows[4058][0]
patch_obj=json.loads(patch_record)
diff=patch_obj['diff']
old="print('VERIFICATION_RESULT: COMPLETED_GENERAL_FTS_STATE_GATE',flush=True)\n"
# Extract replacement from the DB patch tool call is in assistant msg 4057, not tool msg 4058.
tc57=con.execute('select tool_calls from messages where id=4057').fetchone()[0]
pc=json.loads(tc57)[0]
pa=pc.get('function',pc).get('arguments')
if isinstance(pa,str): pa=json.loads(pa)
new=pa['new_string']; old_db=pa['old_string']
reconstructed=source.replace(old_db,new)
current=pathlib.Path(r'D:/Projects/ToE_21st_June_NEWEST/historical_hermes_general_fts_state_recovered.py').read_text(encoding='utf-8')
H=lambda s: hashlib.sha256(s.encode()).hexdigest()
print('source_sha',H(source))
print('patch_tool_content_sha',H(patch_record))
print('patch_diff_sha',H(diff))
print('patch_new_string_sha',H(new))
print('expected_source_sha','0396ff83436190e87696f1ec7f419b18bf3fba604b7e0cb9bf6f064507cff5f9')
print('expected_patch_sha','dab887e511e50ac784c2f09e26d94a40a25c0d7dcda7928fedfa9804cb2af3ac')
print('old_matches',old_db==old,'old_occurrences',source.count(old_db))
print('reconstructed_sha',H(reconstructed))
print('current_text_sha',H(current))
print('current_exact_match',current==reconstructed)
print('terminal_output_contains_6.128', '6.128112419919731e-06' in rows[4060][0])
PY
