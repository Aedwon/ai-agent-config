# Versioning

The repository root `VERSION` file is the canonical release marker for AI Agent
Config. The current v2 architecture starts at `2.0.0`.

AI Agent Config uses semantic versioning for the scaffold itself:

- **Major** versions mark incompatible changes to the policy/composition model,
  manifest contract, or generated configuration contract.
- **Minor** versions add compatible capabilities such as project types,
  workflows, adapters, commands, or meaningful policy improvements.
- **Patch** versions contain compatible fixes, documentation corrections, and
  verification improvements that do not intentionally change the public
  contract.

The scaffold version is independent of provider, model, package, or subscription
versions. A clone can identify the policy/tooling snapshot it started from with:

```sh
cat VERSION
```

Release tags should use the matching `vMAJOR.MINOR.PATCH` form. Before tagging a
release, run the repository self-verification command:

```sh
python3 -m tooling.verify
```

The command validates the version marker, checks whitespace in the selected
diff, runs the unit-test suite, and validates the canonical repository. CI uses
the same entry point so local and hosted verification stay aligned.
