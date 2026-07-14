set -e
LOG='/d/Projects/can_o_worms/chat_artifacts_v1/logs/session_export_run_v1.log'
test ! -e "$LOG"
env -u PYTHONPATH /d/Projects/toe_new/.venv/Scripts/python.exe /d/Projects/can_o_worms/chat_artifacts_v1/tools/extract_current_chat_from_hermes_db_v1.py 2>&1 | tee "$LOG"
