-- ====================================================================
-- 货运代理业务管理系统 - 完整数据库结构
-- Database: tradebusiness
-- MySQL Version: 8.0+
-- Character Set: utf8mb4
-- ====================================================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS tradebusiness
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE tradebusiness;

-- ====================================================================
-- 1. 用户表 (users)
-- ====================================================================
CREATE TABLE IF NOT EXISTS users (
  id CHAR(36) PRIMARY KEY COMMENT 'UUID主键',
  username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名（登录名）',
  email VARCHAR(100) UNIQUE COMMENT '邮箱地址',
  hashed_password VARCHAR(255) NOT NULL COMMENT 'bcrypt加密后的密码',
  full_name VARCHAR(100) COMMENT '真实姓名',
  phone VARCHAR(20) COMMENT '手机号',
  avatar_url VARCHAR(500) COMMENT '头像URL',
  department VARCHAR(100) COMMENT '部门',
  hired_date DATE COMMENT '入职日期',
  resigned_date DATE COMMENT '离职日期',
  notes TEXT COMMENT '备注信息',
  role VARCHAR(20) NOT NULL DEFAULT 'sales' COMMENT '角色：admin/sales',
  is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
  is_superuser TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否超级管理员',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  INDEX idx_role (role),
  INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='系统用户表（管理员和业务员）';

-- ====================================================================
-- 2. 客户表 (customers)
-- ====================================================================
CREATE TABLE IF NOT EXISTS customers (
  id CHAR(36) PRIMARY KEY COMMENT 'UUID主键',

  -- 基本信息
  company_name VARCHAR(200) NOT NULL COMMENT '公司名称',
  company_name_en VARCHAR(200) COMMENT '英文名称',
  company_name_local VARCHAR(200) COMMENT '本地语言名称',
  logo_url VARCHAR(500) COMMENT '公司Logo URL',
  website VARCHAR(200) COMMENT '公司网站',

  -- 公司规模信息
  established_year INT COMMENT '成立年份',
  registered_capital VARCHAR(50) COMMENT '注册资本',
  company_size INT COMMENT '员工人数',
  business_type VARCHAR(50) COMMENT '业务类型：sea/air/land/multimodal',

  -- 业务信息
  main_ports JSON COMMENT '主要经营的港口列表',
  route_coverage JSON COMMENT '航线覆盖范围',
  cargo_specialization JSON COMMENT '货物专业化类型',
  estimated_volume INT COMMENT '预估年货量（TEU）',

  -- 地理位置
  country_code CHAR(3) NOT NULL COMMENT 'ISO 3166-1三位国家代码',
  country VARCHAR(100) NOT NULL COMMENT '国家名称',
  city VARCHAR(100) COMMENT '城市',
  address TEXT COMMENT '详细地址',

  -- 联系方式
  phone VARCHAR(50) COMMENT '电话号码',
  email VARCHAR(100) COMMENT '邮箱地址',
  whatsapp VARCHAR(50) COMMENT 'WhatsApp号码',
  wechat VARCHAR(50) COMMENT '微信号',

  -- 社交媒体
  linkedin_url VARCHAR(200) COMMENT 'LinkedIn主页',
  facebook_url VARCHAR(200) COMMENT 'Facebook主页',

  -- 客户管理
  status VARCHAR(20) NOT NULL DEFAULT 'potential' COMMENT '客户状态：potential/contacting/cooperating/paused/lost',
  assigned_to CHAR(36) COMMENT '分配给的业务员ID',
  priority INT NOT NULL DEFAULT 3 COMMENT '优先级：1-5（1最高）',
  source VARCHAR(100) COMMENT '客户来源',
  source_url VARCHAR(500) COMMENT '来源URL',
  data_confidence INT COMMENT '数据可信度：1-5',
  last_verified_at DATETIME COMMENT '最后验证时间',

  -- 标签和备注
  tags JSON COMMENT '标签列表',
  notes TEXT COMMENT '备注信息',

  -- 重要日期
  first_contact_date DATE COMMENT '首次联系日期',
  cooperation_date DATE COMMENT '开始合作日期',

  -- 时间戳
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  -- 索引
  INDEX idx_company_name (company_name),
  INDEX idx_country_code (country_code),
  INDEX idx_country (country),
  INDEX idx_email (email),
  INDEX idx_status (status),
  INDEX idx_assigned_to (assigned_to),
  INDEX idx_priority (priority),

  -- 外键
  CONSTRAINT fk_customers_assigned_to FOREIGN KEY (assigned_to)
    REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='货运代理公司客户表';

-- ====================================================================
-- 3. 邮件模板表 (email_templates)
-- ====================================================================
CREATE TABLE IF NOT EXISTS email_templates (
  id CHAR(36) PRIMARY KEY COMMENT 'UUID主键',
  name VARCHAR(100) NOT NULL UNIQUE COMMENT '模板名称（唯一）',
  subject VARCHAR(200) NOT NULL COMMENT '邮件主题（支持Jinja2模板）',
  body TEXT NOT NULL COMMENT '邮件内容（HTML+Jinja2模板）',
  category VARCHAR(50) COMMENT '分类：intro/followup/greeting/promotion',
  language VARCHAR(10) NOT NULL DEFAULT 'zh' COMMENT '语言：zh/en/fr/ar',
  variables JSON COMMENT '可用变量说明',
  is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  created_by CHAR(36) COMMENT '创建者用户ID',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  INDEX idx_category (category),
  INDEX idx_is_active (is_active),
  CONSTRAINT fk_email_templates_creator FOREIGN KEY (created_by)
    REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='邮件模板表（Jinja2）';

-- ====================================================================
-- 4. 邮件记录表 (emails)
-- ====================================================================
CREATE TABLE IF NOT EXISTS emails (
  id CHAR(36) PRIMARY KEY COMMENT 'UUID主键',

  -- 关联信息
  customer_id CHAR(36) COMMENT '关联客户ID',
  sender_id CHAR(36) COMMENT '发送者用户ID',
  template_id CHAR(36) COMMENT '使用的模板ID',

  -- 邮件内容
  subject VARCHAR(500) NOT NULL COMMENT '邮件主题',
  body TEXT NOT NULL COMMENT '邮件内容（HTML）',
  direction VARCHAR(20) NOT NULL DEFAULT 'outgoing' COMMENT '方向：outgoing/incoming',
  status VARCHAR(20) NOT NULL DEFAULT 'draft' COMMENT '状态：draft/queued/sent/failed/opened/replied',

  -- 收发件人
  to_email VARCHAR(100) NOT NULL COMMENT '收件人邮箱',
  to_name VARCHAR(100) COMMENT '收件人姓名',
  from_email VARCHAR(100) NOT NULL COMMENT '发件人邮箱',
  from_name VARCHAR(100) COMMENT '发件人姓名',
  template_name VARCHAR(100) COMMENT '使用的模板名称',

  -- 跟踪信息
  sent_at DATETIME COMMENT '发送时间',
  opened_at DATETIME COMMENT '打开时间',
  clicked_at DATETIME COMMENT '点击时间',
  replied_at DATETIME COMMENT '回复时间',
  error_message TEXT COMMENT '错误信息',

  -- SMTP信息
  message_id VARCHAR(200) COMMENT 'SMTP Message-ID',
  thread_id VARCHAR(200) COMMENT '邮件线程ID',
  attachments JSON COMMENT '附件列表',

  -- 时间戳
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  -- 索引
  INDEX idx_customer_id (customer_id),
  INDEX idx_sender_id (sender_id),
  INDEX idx_status (status),
  INDEX idx_direction (direction),
  INDEX idx_template_id (template_id),

  -- 外键
  CONSTRAINT fk_emails_customer FOREIGN KEY (customer_id)
    REFERENCES customers(id) ON DELETE SET NULL,
  CONSTRAINT fk_emails_sender FOREIGN KEY (sender_id)
    REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_emails_template FOREIGN KEY (template_id)
    REFERENCES email_templates(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='邮件记录表';

-- ====================================================================
-- 5. 任务表 (tasks)
-- ====================================================================
CREATE TABLE IF NOT EXISTS tasks (
  id CHAR(36) PRIMARY KEY COMMENT 'UUID主键',
  title VARCHAR(200) NOT NULL COMMENT '任务标题',
  description TEXT COMMENT '任务描述',
  type VARCHAR(50) COMMENT '任务类型：followup/email/meeting/other',
  customer_id CHAR(36) COMMENT '关联客户ID',
  assigned_to CHAR(36) COMMENT '分配给的用户ID',
  created_by CHAR(36) COMMENT '创建者用户ID',
  status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态：pending/in_progress/completed/cancelled',
  priority VARCHAR(20) NOT NULL DEFAULT 'medium' COMMENT '优先级：low/medium/high/urgent',
  due_date DATETIME COMMENT '截止日期',
  completed_at DATETIME COMMENT '完成时间',
  reminder_at DATETIME COMMENT '提醒时间',
  is_reminded TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已提醒',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  INDEX idx_customer_id (customer_id),
  INDEX idx_assigned_to (assigned_to),
  INDEX idx_status (status),
  INDEX idx_priority (priority),
  CONSTRAINT fk_tasks_assigned FOREIGN KEY (assigned_to)
    REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_tasks_creator FOREIGN KEY (created_by)
    REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_tasks_customer FOREIGN KEY (customer_id)
    REFERENCES customers(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='任务管理表';

-- ====================================================================
-- 6. 节假日表 (holidays)
-- ====================================================================
CREATE TABLE IF NOT EXISTS holidays (
  id CHAR(36) PRIMARY KEY COMMENT 'UUID主键',
  country_code CHAR(3) NOT NULL COMMENT 'ISO 3166-1三位国家代码',
  name VARCHAR(100) NOT NULL COMMENT '节假日名称',
  local_name VARCHAR(100) COMMENT '本地语言名称',
  holiday_date DATE NOT NULL COMMENT '节日日期',
  type VARCHAR(20) COMMENT '类型：public_holiday/religious/company',
  is_recurring TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否每年重复',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  INDEX idx_country_code (country_code),
  INDEX idx_holiday_date (holiday_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='全球节假日数据表';

-- ====================================================================
-- 7. 通知表 (notifications)
-- ====================================================================
CREATE TABLE IF NOT EXISTS notifications (
  id CHAR(36) PRIMARY KEY COMMENT 'UUID主键',
  user_id CHAR(36) NOT NULL COMMENT '接收用户ID',
  type VARCHAR(50) NOT NULL COMMENT '通知类型：new_email/task_reminder/task_assigned/system',
  title VARCHAR(200) NOT NULL COMMENT '通知标题',
  message TEXT NOT NULL COMMENT '通知内容',
  data JSON COMMENT '附加数据（JSON格式）',
  is_read TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已读',
  read_at DATETIME COMMENT '阅读时间',
  expires_at DATETIME COMMENT '过期时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  INDEX idx_user_id (user_id),
  INDEX idx_is_read (is_read),
  INDEX idx_type (type),
  CONSTRAINT fk_notifications_user FOREIGN KEY (user_id)
    REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='用户通知表';

-- ====================================================================
-- 8. 数据采集任务表 (scraping_tasks)
-- ====================================================================
CREATE TABLE IF NOT EXISTS scraping_tasks (
  id CHAR(36) PRIMARY KEY COMMENT 'UUID主键',
  name VARCHAR(200) NOT NULL COMMENT '任务名称',
  task_type ENUM('google', 'directory', 'specific_site') NOT NULL COMMENT '任务类型',
  status ENUM('pending', 'running', 'completed', 'failed', 'cancelled')
         NOT NULL DEFAULT 'pending' COMMENT '任务状态',

  config JSON NOT NULL COMMENT '任务配置',
  keywords JSON NOT NULL COMMENT '关键词列表',
  countries JSON NOT NULL COMMENT '国家代码列表',

  total_found INT DEFAULT 0 COMMENT '发现数据总数',
  total_saved INT DEFAULT 0 COMMENT '已保存数据数',
  error_message TEXT NULL COMMENT '错误信息',

  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  started_at DATETIME NULL COMMENT '开始时间',
  completed_at DATETIME NULL COMMENT '完成时间',

  created_by CHAR(36) NOT NULL COMMENT '创建者ID',

  INDEX idx_status (status),
  INDEX idx_task_type (task_type),
  INDEX idx_created_by (created_by),
  INDEX idx_created_at (created_at),

  CONSTRAINT fk_scraping_tasks_creator FOREIGN KEY (created_by)
    REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='数据采集任务表';

-- ====================================================================
-- 初始化数据
-- ====================================================================

-- 插入默认管理员账户
INSERT INTO users (
  id, username, email, hashed_password, full_name, role, is_superuser, is_active
) VALUES (
  '00000000-0000-0000-0000-000000000001',
  'admin',
  'admin@tradebusiness.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpWEmD0Ja',  -- 密码: Admin123
  '系统管理员',
  'admin',
  1,
  1
) ON DUPLICATE KEY UPDATE username=username;

-- 插入默认销售员账户
INSERT INTO users (
  id, username, email, hashed_password, full_name, role, is_superuser, is_active
) VALUES (
  '00000000-0000-0000-0000-000000000002',
  'sales01',
  'sales01@tradebusiness.com',
  '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36UhV0R4C8fK9qG2U0m8EdG',  -- 密码: Sales123
  '销售员01',
  'sales',
  0,
  1
) ON DUPLICATE KEY UPDATE username=username;

-- 插入默认邮件模板
INSERT INTO email_templates (
  id, name, subject, body, category, language, is_active
) VALUES (
  '00000000-0000-0000-0000-000000000010',
  '新客户介绍',
  '介绍 - {{company_name}}',
  '<h2>尊敬的 {{company_name}}：</h2>
  <p>您好！我们是TradeBusiness，一家专业的货运代理公司。</p>
  <p>我们主要提供海运、空运、陆运和多式联运服务。</p>
  <p>希望能有机会与您合作！</p>',
  'intro',
  'zh',
  1
) ON DUPLICATE KEY UPDATE name=name;

-- ====================================================================
-- 完成
-- ====================================================================
-- 数据库初始化完成！
-- 可以使用以下命令验证：
-- SHOW TABLES;
-- SELECT COUNT(*) FROM users;
-- ====================================================================
