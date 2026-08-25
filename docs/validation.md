# Validation

Run the deterministic suite from the repository root:

```sh
git diff --check
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m tooling.config validate --root .
```

The suite covers core separation, authorization invariants, catalog and adapter
schemas, provenance, licenses, ownership classifications, strategy uniqueness,
trigger uniqueness, path containment, forbidden destinations, placeholders,
deterministic rendering, source immutability, migration mappings, and adoption
examples. It uses only the Python standard library and does not require GitHub
Actions.

## Recognition probes

Recognition is separate from static validation because it invokes an already
installed provider executable. Review adapter arguments before opting in:

```sh
python3 -m tests.recognition.run \
  --root . \
  --adapter codex \
  --executable /absolute/path/to/executable
```

Each probe uses fresh temporary positive and negative projects. It appends a
unique marker to the staged positive entry, does not put the marker in the
prompt, and checks that an unrelated project does not report the marker. It
does not copy credentials, select a model or subscription, install a provider,
or load optional skills.

Results are `PASS`, `FAIL`, or `UNPROVEN`. Missing executables, authentication
failures, timeouts, and ambiguous output are `UNPROVEN`, not evidence of
recognition and not a static adapter failure. Generic and Antigravity IDE
adapters are manual and therefore remain `UNPROVEN` until a user follows their
integration instructions. Antigravity CLI is not used to prove IDE discovery.
