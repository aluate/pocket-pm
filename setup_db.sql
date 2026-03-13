-- Pocket PM — Supabase Database Setup
-- Run this in your Supabase project: Dashboard → SQL Editor → New Query → Paste → Run

-- ============================================================
-- 1. JOBS
-- ============================================================
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    its_id TEXT,
    job_name TEXT NOT NULL,
    builder TEXT DEFAULT '',
    client_name TEXT DEFAULT '',
    responsible_pm TEXT DEFAULT 'Karl',
    stage TEXT DEFAULT 'Sales',
    install_type TEXT DEFAULT 'Install',
    install_date DATE,
    installer_crew TEXT DEFAULT '',
    install_status TEXT DEFAULT 'Scheduled',
    source TEXT DEFAULT 'manual',
    notes TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 2. TASKS
-- ============================================================
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    task_type TEXT DEFAULT 'Field',
    assigned_to TEXT DEFAULT 'Karl',
    waiting_on TEXT,
    status TEXT DEFAULT 'Open',
    priority TEXT DEFAULT 'Normal',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- ============================================================
-- 3. PHOTOS
-- task_id is nullable: supports job-level photos without a task
-- ============================================================
CREATE TABLE IF NOT EXISTS photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    file_url TEXT NOT NULL,
    filename TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 4. TASK TEMPLATES
-- ============================================================
CREATE TABLE IF NOT EXISTS task_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name TEXT NOT NULL,
    task_type TEXT NOT NULL,
    title TEXT NOT NULL,
    assigned_to TEXT DEFAULT 'Karl',
    sort_order INT DEFAULT 0
);

-- ============================================================
-- 5. STORAGE BUCKET for photos
-- Run in Supabase Dashboard → Storage → New Bucket
-- Name: job-photos
-- Public: YES (so URLs work without auth)
-- ============================================================

-- ============================================================
-- 6. DISABLE ROW LEVEL SECURITY (single-user app, no auth)
-- ============================================================
ALTER TABLE jobs DISABLE ROW LEVEL SECURITY;
ALTER TABLE tasks DISABLE ROW LEVEL SECURITY;
ALTER TABLE photos DISABLE ROW LEVEL SECURITY;
ALTER TABLE task_templates DISABLE ROW LEVEL SECURITY;
