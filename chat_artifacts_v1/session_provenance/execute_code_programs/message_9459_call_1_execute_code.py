from hermes_tools import terminal
r=terminal("env -u PYTHONPATH /d/Projects/toe_new/.venv/Scripts/python.exe -c \"import json, fts_moment_map_extraction as f; print(json.dumps(f.diagnostic_ckm_reproduction(), indent=2))\"", timeout=300, workdir="D:/Projects/ToE_21st_June_NEWEST")
print(r['output'])