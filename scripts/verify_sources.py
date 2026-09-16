#!/usr/bin/env python3
"""Compare vendored Lean files with the recorded upstream source hashes."""
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
provenance = json.loads((ROOT/'upstream/provenance.json').read_text())
changes = {}
for variant, spec in provenance.items():
    changed = []
    for module, expected in spec['source_sha256'].items():
        path = ROOT/variant/(module.replace('.', '/')+'.lean')
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        if actual != expected: changed.append({'module': module, 'upstream_sha256': expected, 'current_sha256': actual})
    changes[variant] = changed
print(json.dumps(changes, indent=2))
