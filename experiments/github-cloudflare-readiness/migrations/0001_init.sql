CREATE TABLE webhook_deliveries (
  delivery_id TEXT PRIMARY KEY,
  event_name TEXT NOT NULL,
  repo_full_name TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('accepted', 'completed', 'ignored', 'failed')),
  received_at TEXT NOT NULL,
  completed_at TEXT,
  last_error TEXT
);

CREATE INDEX idx_webhook_deliveries_received_at
  ON webhook_deliveries(received_at);

CREATE TABLE repo_policies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  repo_full_name TEXT NOT NULL,
  branch_glob TEXT NOT NULL,
  protected_base_sha TEXT NOT NULL,
  allowed_paths_json TEXT NOT NULL DEFAULT '[]',
  integration_branch TEXT,
  priority INTEGER NOT NULL DEFAULT 0,
  enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
  UNIQUE(repo_full_name, branch_glob)
);

CREATE INDEX idx_repo_policies_repo_enabled
  ON repo_policies(repo_full_name, enabled, priority DESC);

CREATE TABLE branch_state (
  repo_full_name TEXT NOT NULL,
  branch_name TEXT NOT NULL,
  head_sha TEXT NOT NULL,
  protected_base_sha TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('READY_FOR_VERIFICATION', 'ATTENTION', 'BLOCKED')),
  ahead_by INTEGER NOT NULL,
  behind_by INTEGER NOT NULL,
  changed_files INTEGER NOT NULL,
  scope_violations INTEGER NOT NULL,
  reasons_json TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY(repo_full_name, branch_name)
);

CREATE INDEX idx_branch_state_status_updated
  ON branch_state(status, updated_at DESC);
