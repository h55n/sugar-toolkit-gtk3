"""Fail unless the old regression is observed and repaired matrix is green."""
import os
from pathlib import Path
import subprocess
import sys

root = Path.cwd()
logs = root / 'proof/logs'
logs.mkdir(parents=True, exist_ok=True)
source = root / 'src/sugar3/presence/connectionmanager.py'
fixed = source.read_bytes()
old = subprocess.check_output(['git', 'show', 'd18779f6b712584d75847facdec28550f58b3871:src/sugar3/presence/connectionmanager.py'])

def run(name):
    result = subprocess.run(['xvfb-run', '-a', 'dbus-run-session', '--',
                             'bash', 'proof/run-suite.sh'],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (logs / (name + '.log')).write_bytes(result.stdout)
    print(name, 'exit', result.returncode, flush=True)
    return result

try:
    # Honest original full-suite result is evidence, not silently greenwashed.
    result = run('exact450-unmodified-baseline')
    if result.returncode == 0:
        print('Baseline changed: inspect before using old expectations.', file=sys.stderr)
        sys.exit(1)
    subprocess.run(['git', 'apply', 'proof/baseline-compatibility.patch'], check=True)
    source.write_bytes(old)
    result = run('old-code-with-compatible-baseline')
    if result.returncode != 1 or b'FAILED (errors=1)' not in result.stdout or b'test_status_changed_for_untracked_account_is_ignored' not in result.stdout:
        sys.exit('Expected one old-code regression, not unrelated failures.')
    source.write_bytes(fixed)
    result = run('fixed-with-compatible-baseline')
    if result.returncode != 0 or b'Ran 24 tests' not in result.stdout or b'\nOK\n' not in result.stdout:
        sys.exit('Fixed compatibility matrix did not pass all 24 tests.')
finally:
    source.write_bytes(fixed)
