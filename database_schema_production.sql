-- TradeBusiness 正式环境完整数据库结构
-- 版本：2026-07-17
-- MySQL 8.0+ / utf8mb4
-- 本文件用于新数据库初始化，不包含测试数据和默认密码。

CREATE DATABASE IF NOT EXISTS tradebusiness CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tradebusiness;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS users (
  id CHAR(36) NOT NULL, username VARCHAR(50) NOT NULL, email VARCHAR(100) NOT NULL,
  hashed_password VARCHAR(200) NOT NULL, full_name VARCHAR(100), `role` VARCHAR(20) NOT NULL DEFAULT 'sales',
  is_active BOOLEAN NOT NULL DEFAULT TRUE, is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
  phone VARCHAR(20), avatar_url VARCHAR(500), department VARCHAR(100), hired_date DATE,
  resigned_date DATE, notes TEXT, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id),
  UNIQUE KEY uk_users_username (username), UNIQUE KEY uk_users_email (email),
  KEY ix_users_is_active (is_active), KEY ix_users_role (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS holidays (
  id CHAR(36) NOT NULL, country_code VARCHAR(3) NOT NULL, name VARCHAR(100) NOT NULL,
  local_name VARCHAR(100), holiday_date DATE NOT NULL, type VARCHAR(20),
  is_recurring BOOLEAN NOT NULL DEFAULT FALSE, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id),
  KEY ix_holidays_country_code (country_code), KEY ix_holidays_holiday_date (holiday_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS subscription_plans (
  id CHAR(36) NOT NULL, name VARCHAR(80) NOT NULL, price INT NOT NULL DEFAULT 0,
  credits INT NOT NULL DEFAULT 0, `interval` VARCHAR(20) NOT NULL DEFAULT 'month',
  is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id),
  UNIQUE KEY uk_subscription_plans_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS customers (
  id CHAR(36) NOT NULL, company_name VARCHAR(200) NOT NULL, company_name_en VARCHAR(200),
  company_name_local VARCHAR(200), logo_url VARCHAR(500), website VARCHAR(200), established_year INT,
  registered_capital VARCHAR(50), company_size INT, business_type VARCHAR(50), main_ports JSON,
  route_coverage JSON, cargo_specialization JSON, estimated_volume INT, country_code VARCHAR(3) NOT NULL,
  country VARCHAR(100) NOT NULL, city VARCHAR(100), address TEXT, phone VARCHAR(50), email VARCHAR(100),
  whatsapp VARCHAR(50), wechat VARCHAR(50), linkedin_url VARCHAR(200), facebook_url VARCHAR(200),
  status VARCHAR(20) NOT NULL DEFAULT 'potential', assigned_to CHAR(36), priority INT NOT NULL DEFAULT 3,
  source VARCHAR(100), source_url VARCHAR(500), data_confidence INT, last_verified_at DATETIME,
  tags JSON, notes TEXT, first_contact_date DATE, cooperation_date DATE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id), KEY ix_customers_company_name (company_name), KEY ix_customers_business_type (business_type),
  KEY ix_customers_country_code (country_code), KEY ix_customers_country (country), KEY ix_customers_email (email),
  KEY ix_customers_status (status), KEY ix_customers_assigned_to (assigned_to),
  CONSTRAINT fk_customers_assigned_to FOREIGN KEY (assigned_to) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS email_templates (
  id CHAR(36) NOT NULL, name VARCHAR(100) NOT NULL, subject VARCHAR(200) NOT NULL, body TEXT NOT NULL,
  category VARCHAR(50), language VARCHAR(10) NOT NULL DEFAULT 'zh', variables JSON,
  is_active BOOLEAN NOT NULL DEFAULT TRUE, created_by CHAR(36),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id), UNIQUE KEY uk_email_templates_name (name), KEY ix_email_templates_category (category),
  CONSTRAINT fk_email_templates_created_by FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS lead_search_tasks (
  id CHAR(36) NOT NULL, user_id CHAR(36) NOT NULL, name VARCHAR(200) NOT NULL,
  target_country VARCHAR(100), target_industry VARCHAR(120), product_keywords JSON, customer_profile TEXT,
  exclude_keywords JSON, website_inputs JSON, status VARCHAR(20) NOT NULL DEFAULT 'pending',
  total_found INT NOT NULL DEFAULT 0, error_message TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id), KEY ix_lead_search_tasks_user_id (user_id), KEY ix_lead_search_tasks_name (name),
  KEY ix_lead_search_tasks_target_country (target_country), KEY ix_lead_search_tasks_target_industry (target_industry),
  KEY ix_lead_search_tasks_status (status),
  CONSTRAINT fk_lead_search_tasks_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sales_agents (
  id CHAR(36) NOT NULL, user_id CHAR(36) NOT NULL, name VARCHAR(120) NOT NULL, company_intro TEXT,
  product_intro TEXT, value_proposition TEXT, target_customer TEXT, tone VARCHAR(50) NOT NULL DEFAULT 'professional',
  forbidden_words TEXT, default_language VARCHAR(20) NOT NULL DEFAULT 'en', is_default BOOLEAN NOT NULL DEFAULT FALSE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id), KEY ix_sales_agents_user_id (user_id),
  CONSTRAINT fk_sales_agents_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS scraping_tasks (
  id CHAR(36) NOT NULL, name VARCHAR(200) NOT NULL, task_type VARCHAR(50) NOT NULL, status VARCHAR(20) NOT NULL,
  config JSON NOT NULL, keywords JSON NOT NULL, countries JSON NOT NULL, total_found INT NOT NULL DEFAULT 0,
  total_saved INT NOT NULL DEFAULT 0, error_message TEXT, started_at DATETIME, completed_at DATETIME,
  created_by CHAR(36) NOT NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS scraped_leads (
  id CHAR(36) NOT NULL, raw_data JSON NOT NULL, data_source VARCHAR(50) NOT NULL, source_url VARCHAR(500),
  company_name VARCHAR(200) NOT NULL, company_name_en VARCHAR(200), country VARCHAR(100) NOT NULL,
  country_code VARCHAR(3) NOT NULL, city VARCHAR(100), email VARCHAR(100), phone VARCHAR(50), whatsapp VARCHAR(50),
  website VARCHAR(200), business_type VARCHAR(50), description TEXT, confidence_score INT NOT NULL DEFAULT 0,
  status VARCHAR(20) NOT NULL DEFAULT 'pending', reviewed_by CHAR(36), reviewed_at DATETIME, rejection_reason TEXT,
  imported_to_customer_id CHAR(36), imported_at DATETIME, scraping_task_id CHAR(36) NOT NULL,
  matched_by CHAR(36), duplicate_of CHAR(36), similarity_score INT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id), KEY ix_scraped_leads_company_name (company_name), KEY ix_scraped_leads_country_code (country_code),
  KEY ix_scraped_leads_scraping_task (scraping_task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS agent_knowledge_documents (
  id CHAR(36) NOT NULL, agent_id CHAR(36) NOT NULL, file_name VARCHAR(255) NOT NULL, content_text TEXT NOT NULL,
  embedding_status VARCHAR(30) NOT NULL DEFAULT 'pending', created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id), KEY ix_agent_knowledge_documents_agent_id (agent_id),
  CONSTRAINT fk_agent_knowledge_documents_agent_id FOREIGN KEY (agent_id) REFERENCES sales_agents (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS agent_prompt_templates (
  id CHAR(36) NOT NULL, agent_id CHAR(36) NOT NULL, name VARCHAR(120) NOT NULL, channel VARCHAR(30) NOT NULL,
  language VARCHAR(20) NOT NULL, prompt_text TEXT NOT NULL, is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id), KEY ix_agent_prompt_templates_agent_id (agent_id),
  CONSTRAINT fk_agent_prompt_templates_agent_id FOREIGN KEY (agent_id) REFERENCES sales_agents (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS credit_wallets (
  id CHAR(36) NOT NULL, user_id CHAR(36) NOT NULL, balance INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id), UNIQUE KEY uk_credit_wallets_user_id (user_id),
  CONSTRAINT fk_credit_wallets_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS credit_transactions (
  id CHAR(36) NOT NULL, user_id CHAR(36) NOT NULL, amount INT NOT NULL, balance_after INT NOT NULL,
  action VARCHAR(50) NOT NULL, description TEXT, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id), KEY ix_credit_transactions_user_id (user_id),
  CONSTRAINT fk_credit_transactions_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS user_subscriptions (
  id CHAR(36) NOT NULL, user_id CHAR(36) NOT NULL, plan_id CHAR(36) NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'active', created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id),
  UNIQUE KEY uk_user_subscriptions_user_id (user_id), KEY ix_user_subscriptions_plan_id (plan_id),
  CONSTRAINT fk_user_subscriptions_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
  CONSTRAINT fk_user_subscriptions_plan_id FOREIGN KEY (plan_id) REFERENCES subscription_plans (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS payment_orders (
  id CHAR(36) NOT NULL, user_id CHAR(36) NOT NULL, plan_id CHAR(36) NOT NULL, amount INT NOT NULL,
  provider VARCHAR(30) NOT NULL DEFAULT 'pending', status VARCHAR(30) NOT NULL DEFAULT 'pending', external_id VARCHAR(200),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id), KEY ix_payment_orders_user_id (user_id), KEY ix_payment_orders_plan_id (plan_id),
  KEY ix_payment_orders_status (status),
  CONSTRAINT fk_payment_orders_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
  CONSTRAINT fk_payment_orders_plan_id FOREIGN KEY (plan_id) REFERENCES subscription_plans (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS notifications (
  id CHAR(36) NOT NULL, user_id CHAR(36) NOT NULL, type VARCHAR(50) NOT NULL, title VARCHAR(200) NOT NULL,
  message VARCHAR(1000) NOT NULL, data JSON, is_read BOOLEAN NOT NULL DEFAULT FALSE, read_at DATETIME,
  expires_at DATETIME, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id), KEY ix_notifications_user_id (user_id),
  KEY ix_notifications_type (type), KEY ix_notifications_is_read (is_read),
  CONSTRAINT fk_notifications_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS emails (
  id CHAR(36) NOT NULL, customer_id CHAR(36), sender_id CHAR(36), subject VARCHAR(500) NOT NULL, body TEXT NOT NULL,
  direction VARCHAR(20) NOT NULL DEFAULT 'outgoing', status VARCHAR(20) NOT NULL DEFAULT 'draft',
  to_email VARCHAR(100) NOT NULL, to_name VARCHAR(100), from_email VARCHAR(100) NOT NULL, from_name VARCHAR(100),
  template_id CHAR(36), template_name VARCHAR(100), sent_at DATETIME, opened_at DATETIME, clicked_at DATETIME,
  replied_at DATETIME, error_message TEXT, message_id VARCHAR(200), thread_id VARCHAR(200), attachments JSON,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id), KEY ix_emails_customer_id (customer_id), KEY ix_emails_sender_id (sender_id), KEY ix_emails_status (status),
  CONSTRAINT fk_emails_customer_id FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE SET NULL,
  CONSTRAINT fk_emails_sender_id FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE SET NULL,
  CONSTRAINT fk_emails_template_id FOREIGN KEY (template_id) REFERENCES email_templates (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS leads (
  id CHAR(36) NOT NULL, task_id CHAR(36), user_id CHAR(36) NOT NULL, company_name VARCHAR(200) NOT NULL,
  website VARCHAR(500), country VARCHAR(100), industry VARCHAR(120), description TEXT, source VARCHAR(100),
  match_score FLOAT, status VARCHAR(30) NOT NULL DEFAULT 'potential', do_not_contact BOOLEAN NOT NULL DEFAULT FALSE,
  do_not_contact_reason VARCHAR(300), notes TEXT, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id), KEY ix_leads_task_id (task_id),
  KEY ix_leads_user_id (user_id), KEY ix_leads_company_name (company_name), KEY ix_leads_website (website),
  KEY ix_leads_country (country), KEY ix_leads_industry (industry), KEY ix_leads_status (status),
  KEY ix_leads_do_not_contact (do_not_contact),
  CONSTRAINT fk_leads_task_id FOREIGN KEY (task_id) REFERENCES lead_search_tasks (id) ON DELETE SET NULL,
  CONSTRAINT fk_leads_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS lead_contacts (
  id CHAR(36) NOT NULL, lead_id CHAR(36) NOT NULL, name VARCHAR(120), title VARCHAR(120), email VARCHAR(120),
  phone VARCHAR(60), linkedin_url VARCHAR(500), whatsapp VARCHAR(60), source VARCHAR(100),
  is_verified BOOLEAN NOT NULL DEFAULT FALSE, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id), KEY ix_lead_contacts_lead_id (lead_id),
  KEY ix_lead_contacts_email (email),
  CONSTRAINT fk_lead_contacts_lead_id FOREIGN KEY (lead_id) REFERENCES leads (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS company_research_reports (
  id CHAR(36) NOT NULL, lead_id CHAR(36) NOT NULL, summary TEXT NOT NULL, business_model TEXT, products TEXT,
  target_markets TEXT, buying_signals TEXT, pain_points TEXT, recommended_angle TEXT, raw_sources JSON,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id), KEY ix_company_research_reports_lead_id (lead_id),
  CONSTRAINT fk_company_research_reports_lead_id FOREIGN KEY (lead_id) REFERENCES leads (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sales_copies (
  id CHAR(36) NOT NULL, lead_id CHAR(36) NOT NULL, channel VARCHAR(30) NOT NULL, language VARCHAR(20) NOT NULL,
  subject VARCHAR(300), content TEXT NOT NULL, tone VARCHAR(50), status VARCHAR(30) NOT NULL DEFAULT 'draft',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id), KEY ix_sales_copies_lead_id (lead_id), KEY ix_sales_copies_channel (channel),
  CONSTRAINT fk_sales_copies_lead_id FOREIGN KEY (lead_id) REFERENCES leads (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS followup_tasks (
  id CHAR(36) NOT NULL, lead_id CHAR(36) NOT NULL, user_id CHAR(36) NOT NULL, channel VARCHAR(30) NOT NULL,
  subject VARCHAR(300), content TEXT NOT NULL, due_at DATETIME NOT NULL, status VARCHAR(30) NOT NULL DEFAULT 'pending',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id), KEY ix_followup_tasks_lead_id (lead_id), KEY ix_followup_tasks_user_id (user_id),
  KEY ix_followup_tasks_due_at (due_at), KEY ix_followup_tasks_status (status),
  CONSTRAINT fk_followup_tasks_lead_id FOREIGN KEY (lead_id) REFERENCES leads (id) ON DELETE CASCADE,
  CONSTRAINT fk_followup_tasks_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tasks (
  id CHAR(36) NOT NULL, title VARCHAR(200) NOT NULL, description TEXT, type VARCHAR(50), customer_id CHAR(36),
  assigned_to CHAR(36), created_by CHAR(36), status VARCHAR(20) NOT NULL DEFAULT 'pending',
  priority VARCHAR(20) NOT NULL DEFAULT 'medium', due_date DATETIME, completed_at DATETIME, reminder_at DATETIME,
  is_reminded BOOLEAN NOT NULL DEFAULT FALSE, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id), KEY ix_tasks_customer_id (customer_id),
  KEY ix_tasks_assigned_to (assigned_to), KEY ix_tasks_status (status),
  CONSTRAINT fk_tasks_customer_id FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE SET NULL,
  CONSTRAINT fk_tasks_assigned_to FOREIGN KEY (assigned_to) REFERENCES users (id) ON DELETE SET NULL,
  CONSTRAINT fk_tasks_created_by FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
-- 默认管理员请运行：cd tradebusiness-backend && python scripts/init_db.py
