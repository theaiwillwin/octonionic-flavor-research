from pathlib import Path
import os

needles = [
    '6.13e-6',
    '0.3887831255',
    '0.2372949892',
    '0.2822870282',
    '0.5117538711',
    '6.13e-06',
    'general-fts-state',
    'locked_jordan_data',
    'fts_moment_map_extraction',
    '0.97435246',
    '0.22499704',
    '0.00369001',
    '0.00856999',
    '0.04109930',
    '0.99911831',
    'r\\simeq',
    '0.3887831255+0.2822870282',
    '0.2372949892-0.5117538711',
    'generating script',
    'UNVERIFIED',
]

roots = [
    Path('D:/Projects/non_associative_ai_claude'),
    Path('C:/Users/theai/stage_h_test'),
    Path('C:/Users/theai/AppData/Local/hermes/profiles/d-drive-profile'),
    Path('C:/Users/theai/AppData/Local/Temp'),
]

matches = []
for root in roots:
    if not root.exists():
        continue
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            p = Path(dirpath) / f
            if p.suffix.lower() not in {
                '.py', '.md', '.tex', '.json', '.txt', '.log',
                '.tar.gz', '.gz', '.tar', '.zip', '.7z', '.rar',
                '.csv', '.yaml', '.yml', '.toml',
            }:
                continue
            try:
                txt = p.read_text(errors='ignore')
            except PermissionError:
                continue
            hits = [n for n in needles if n in txt]
            if hits:
                matches.append((str(p), hits))

print('matches', len(matches))
for p, hits in matches[:200]:
    print(p)
    for h in hits:
        print('  HIT:', h)
if not matches:
    print('NO_MATCHES')
