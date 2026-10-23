PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS clients (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 company_name TEXT NOT NULL,
 industry TEXT NOT NULL DEFAULT '',
 category TEXT NOT NULL DEFAULT '',
 website_url TEXT NOT NULL DEFAULT '',
 website_status TEXT NOT NULL DEFAULT 'Unknown',
 location TEXT NOT NULL DEFAULT '',
 company_description TEXT NOT NULL DEFAULT '',
 products_services TEXT NOT NULL DEFAULT '',
 pricing TEXT NOT NULL DEFAULT '',
 usp TEXT NOT NULL DEFAULT '',
 target_audience TEXT NOT NULL DEFAULT '',
 ideal_customer_profile TEXT NOT NULL DEFAULT '',
 pain_points TEXT NOT NULL DEFAULT '',
 competitors TEXT NOT NULL DEFAULT '',
 objectives TEXT NOT NULL DEFAULT '',
 monthly_budget REAL,
 preferred_language TEXT NOT NULL DEFAULT 'English',
 brand_voice TEXT NOT NULL DEFAULT 'Professional',
 brand_guidelines TEXT NOT NULL DEFAULT '',
 prohibited_topics TEXT NOT NULL DEFAULT '',
 contact_details TEXT NOT NULL DEFAULT '',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS social_accounts (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
 platform TEXT NOT NULL,
 account_status TEXT NOT NULL DEFAULT 'Unknown' CHECK(account_status IN ('Present','Absent','Unknown','Not assessed')),
 profile_url TEXT NOT NULL DEFAULT '',
 activity_status TEXT NOT NULL DEFAULT 'Unknown',
 followers INTEGER,
 posting_frequency TEXT NOT NULL DEFAULT '',
 engagement_metrics TEXT NOT NULL DEFAULT '',
 last_reviewed TEXT NOT NULL DEFAULT '',
 data_source TEXT NOT NULL DEFAULT '',
 verification_status TEXT NOT NULL DEFAULT 'Not verified',
 notes TEXT NOT NULL DEFAULT '',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(client_id, platform)
);
CREATE TABLE IF NOT EXISTS strategies (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
 title TEXT NOT NULL,
 objective TEXT NOT NULL DEFAULT '',
 duration_days INTEGER NOT NULL DEFAULT 30,
 strategy_json TEXT NOT NULL,
 source TEXT NOT NULL DEFAULT 'ollama',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS campaigns (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
 strategy_id INTEGER REFERENCES strategies(id) ON DELETE SET NULL,
 name TEXT NOT NULL,
 objective TEXT NOT NULL DEFAULT '',
 start_date TEXT NOT NULL DEFAULT '',
 end_date TEXT NOT NULL DEFAULT '',
 budget REAL,
 status TEXT NOT NULL DEFAULT 'Draft',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS content_items (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
 strategy_id INTEGER REFERENCES strategies(id) ON DELETE SET NULL,
 campaign_id INTEGER REFERENCES campaigns(id) ON DELETE SET NULL,
 title TEXT NOT NULL,
 platform TEXT NOT NULL,
 content_type TEXT NOT NULL,
 topic TEXT NOT NULL DEFAULT '',
 objective TEXT NOT NULL DEFAULT '',
 caption TEXT NOT NULL DEFAULT '',
 content_json TEXT NOT NULL DEFAULT '{}',
 scheduled_date TEXT,
 status TEXT NOT NULL DEFAULT 'Draft' CHECK(status IN ('Draft','Pending Approval','Approved','Rejected','Scheduled','Published')),
 approval_status TEXT NOT NULL DEFAULT 'Not submitted',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 published_at TEXT,
 external_publish_reference TEXT,
 generation_key TEXT
);
CREATE INDEX IF NOT EXISTS idx_content_client_date ON content_items(client_id, scheduled_date);
CREATE INDEX IF NOT EXISTS idx_content_status ON content_items(status);
CREATE TABLE IF NOT EXISTS content_revisions (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 content_id INTEGER NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
 revision_number INTEGER NOT NULL,
 content_json TEXT NOT NULL,
 comment TEXT NOT NULL DEFAULT '',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(content_id, revision_number)
);
CREATE TABLE IF NOT EXISTS approvals (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 content_id INTEGER NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
 decision TEXT NOT NULL,
 comment TEXT NOT NULL DEFAULT '',
 reviewer TEXT NOT NULL DEFAULT 'Agency reviewer',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS schedules (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 content_id INTEGER NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
 scheduled_for TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'Ready for external scheduling',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(content_id, scheduled_for)
);
CREATE TABLE IF NOT EXISTS performance_metrics (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
 content_id INTEGER REFERENCES content_items(id) ON DELETE SET NULL,
 platform TEXT NOT NULL,
 period_start TEXT NOT NULL,
 period_end TEXT NOT NULL,
 reach INTEGER NOT NULL DEFAULT 0,
 impressions INTEGER NOT NULL DEFAULT 0,
 likes INTEGER NOT NULL DEFAULT 0,
 comments INTEGER NOT NULL DEFAULT 0,
 shares INTEGER NOT NULL DEFAULT 0,
 clicks INTEGER NOT NULL DEFAULT 0,
 leads INTEGER NOT NULL DEFAULT 0,
 spend REAL NOT NULL DEFAULT 0,
 source_label TEXT NOT NULL DEFAULT 'Manually entered',
 notes TEXT NOT NULL DEFAULT '',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS reports (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
 title TEXT NOT NULL,
 period_start TEXT NOT NULL,
 period_end TEXT NOT NULL,
 report_text TEXT NOT NULL,
 data_json TEXT NOT NULL DEFAULT '{}',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
