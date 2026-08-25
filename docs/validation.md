# Validation

Run the deterministic suite from the repository root:

```sh
git diff --check
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m tooling.config validate --root .
```

The suite covers core separation, authorization invariants, catalog and adapter
metadata, provenance, licenses, ownership classifications, strategy uniqueness,
trigger uniqueness, path containment, forbidden destinations, placeholders,
deterministic rendering, manifest and profile composition, source immutability,
migration mappings, and adoption examples. It uses only the Python standard
library and does not require GitHub Actions.

`adapters/catalog.schema.json` is the published machine-readable adapter shape.
The zero-dependency validator manually enforces the safety-critical constraints
used by this repository, but it is not advertised as a complete JSON Schema
engine. Maintainers should keep the manual checks and schema aligned when the
adapter format changes.

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

Instruction discovery proves behavioral context loading, not hard security
enforcement. Use provider-native permissions, hooks, settings, or sandboxing
for controls that must be technically enforced.
