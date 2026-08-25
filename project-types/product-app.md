# Product Application Overlay

Baseline: `software-project.md`

Add these rules for an interactive product that stores user state.

- Design loading, empty, error, success, and recovery states together.
- Preserve user data across schema changes; define migration and rollback
  behavior before altering persistent state.
- Make state persistence, synchronization, and conflict ownership explicit.
- Support keyboard operation, semantic structure, accessible names, visible
  focus, and appropriate contrast.
- Separate release compatibility from implementation completion. Verify upgrade
  and downgrade risks when stored state crosses versions.
- Treat destructive user actions as deliberate flows with confirmation or a
  practical recovery path.
