from af_data import find_af_onsets, load_record, get_rhythm_annotations
import numpy as np

signal, fs, ann = load_record('data/afdb/04015')
print(f'Record 04015 loaded: {len(signal)} samples at {fs} Hz')

onsets = find_af_onsets(ann)
print(f'Found {len(onsets)} AF onsets:')
for i, onset in enumerate(onsets[:5]):
    print(f'  Onset {i}: sample index {onset}')

rhythm = get_rhythm_annotations(len(signal), ann)
print(f'Rhythm array: {len(rhythm)} samples')
print(f'Unique rhythm labels: {set(rhythm)}')
n_count = np.sum(rhythm == 'N')
afib_count = np.sum(rhythm == 'AFIB')
print(f'N-rhythm count: {n_count}')
print(f'AFIB count: {afib_count}')
