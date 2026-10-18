# Prototype unit-suite record (read-only)

Date: 2026-10-18. Prototype HEAD `fdc3362b2418b316e16d6dfd68435e40c1b1afb8`; tracked work
tree clean before and after. No prototype file was modified.

Command (from the prototype root):

```bash
PY=/Users/gzhlaker/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -m unittest discover -s tests -t .
```

Environment: macOS arm64, Python 3.12, NumPy 2.3.5; no CUDA/GPU.

Result:

```text
Ran 646 tests in 78.365s

OK (skipped=10)
```

The 10 skips are CUDA tests; no GPU kernel was executed. The full local log is
`evidence/prototype_tests.log` (ignored by the repository's `*.log` rule; regenerate with the
command above). This is an engineering test record, not benchmark evidence: it does not run
VCSL pairs, a model checkpoint or a full evaluator file comparison.

Round-three interpretation: the suite confirms that the existing prototype is internally
consistent enough to probe, not that the proposed zero-floor recurrence, distinct support,
zero margin or output threshold are implemented. Those remain specification items; see
`evidence/spec_code_contract.md`.
