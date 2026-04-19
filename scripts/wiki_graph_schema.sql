-- Wiki Graph Governance Schema
-- Phase 0 storage substrate (property graph in relational form)

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS nodes(
  id TEXT PRIMARY KEY,
  label TEXT,
  node_type TEXT,
  node_kind TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  metadata TEXT
);

CREATE TABLE IF NOT EXISTS edges(
  id TEXT PRIMARY KEY,
  src TEXT REFERENCES nodes(id),
  dst TEXT REFERENCES nodes(id),
  relation_type TEXT,
  weight DOUBLE PRECISION,
  created_at TIMESTAMP,
  metadata TEXT
);

CREATE TABLE IF NOT EXISTS node_metrics(
  node_id TEXT REFERENCES nodes(id),
  degree DOUBLE PRECISION,
  betweenness DOUBLE PRECISION,
  closeness DOUBLE PRECISION,
  pagerank DOUBLE PRECISION,
  community_id TEXT,
  classification TEXT,
  PRIMARY KEY(node_id)
);

CREATE TABLE IF NOT EXISTS governance_events(
  id TEXT PRIMARY KEY,
  actor_node_id TEXT REFERENCES nodes(id),
  source_state TEXT,
  target_state TEXT,
  signal TEXT,
  sanction_type TEXT,
  duration_seconds DOUBLE PRECISION,
  cooldown_seconds DOUBLE PRECISION,
  audit_required INTEGER,
  automatic_or_manual TEXT,
  created_at TIMESTAMP,
  metadata TEXT
);

CREATE TABLE IF NOT EXISTS graph_change_proposals(
  id TEXT PRIMARY KEY,
  proposer_node_id TEXT REFERENCES nodes(id),
  change_type TEXT,
  status TEXT,
  proposed_at TIMESTAMP,
  reviewed_at TIMESTAMP,
  approved_by TEXT,
  metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_nodes_node_type ON nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_node_kind ON nodes(node_kind);
CREATE INDEX IF NOT EXISTS idx_edges_relation_type ON edges(relation_type);
CREATE INDEX IF NOT EXISTS idx_edges_src ON edges(src);
CREATE INDEX IF NOT EXISTS idx_edges_dst ON edges(dst);
CREATE INDEX IF NOT EXISTS idx_node_metrics_pagerank ON node_metrics(pagerank);
CREATE INDEX IF NOT EXISTS idx_node_metrics_betweenness ON node_metrics(betweenness);
CREATE INDEX IF NOT EXISTS idx_node_metrics_community ON node_metrics(community_id);
