from pathlib import Path

print('=== TRAINING OUTPUT LOCATIONS ===\n')

# Checkpoint Directory
print('1. CHECKPOINT DIRECTORY (Model weights & training history)')
cp = Path('models/checkpoints')
print(f'   Location: {cp.absolute()}')
print(f'   Exists: {cp.exists()}')
if cp.exists():
    files = list(cp.glob('*'))
    print(f'   Total files: {len(files)}')
    if files:
        print('   Recent files:')
        for f in sorted(files)[-5:]:
            size_kb = f.stat().st_size / 1024
            print(f'     - {f.name} ({size_kb:.1f} KB)')

# Logs Directory
print('\n2. LOGS DIRECTORY (Metrics & evaluation data)')
lp = Path('logs')
print(f'   Location: {lp.absolute()}')
print(f'   Exists: {lp.exists()}')
if lp.exists():
    files = list(lp.glob('*'))
    print(f'   Total files: {len(files)}')
    if files:
        print('   Recent files:')
        for f in sorted(files)[-5:]:
            size_kb = f.stat().st_size / 1024
            print(f'     - {f.name} ({size_kb:.1f} KB)')

# Recordings Directory
print('\n3. RECORDINGS DIRECTORY (Game recordings for visualization)')
rp = Path('recordings')
print(f'   Location: {rp.absolute()}')
print(f'   Exists: {rp.exists()}')
if rp.exists():
    files = list(rp.glob('*.json'))
    print(f'   Total recordings: {len(files)}')
    if files:
        print('   Recent recordings:')
        for f in sorted(files)[-5:]:
            size_kb = f.stat().st_size / 1024
            print(f'     - {f.name} ({size_kb:.1f} KB)')

print('\n' + '='*60)
