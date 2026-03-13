# Pocket PM — Build Roadmap

> **For Cursor / future dev sessions:** This document describes the full architecture and remaining work.
> The core scaffold is complete. Use this to continue building phase by phase.

---

## What's Already Built

```
pocket-pm/
├── app.py                      ✅ Main router, top nav
├── core/
│   ├── constants.py            ✅ STAGES, ROLES, TASK_TYPES, aging thresholds
│   ├── supabase_client.py      ✅ Singleton Supabase connection
│   ├── jobs.py                 ✅ Job CRUD, install filtering
│   ├── tasks.py                ✅ Task CRUD, aging logic, get_age_indicator()
│   ├── photos.py               ✅ Photo upload to Supabase Storage
│   └── templates.py            ✅ Template seed + retrieval
├── pages/
│   ├── home.py                 ✅ Dashboard: My Tasks, Waiting, Install Schedule, Quick Add
│   ├── jobs_kanban.py          ✅ 6-column Kanban, New Job form with template selection
│   ├── job_detail.py           ✅ Tasks by type, delegate, complete, edit job, photos
│   ├── task_queue.py           ✅ My Tasks / Team Tasks / Waiting tabs with aging colors
│   ├── install_calendar.py     ✅ Weekly calendar, schedule/status update
│   └── settings.py             ✅ Template viewer, seed button, connection test
├── setup_db.sql                ✅ SQL to create all tables (run in Supabase)
├── Procfile                    ✅ Railway start command
├── requirements.txt            ✅
└── .env                        ✅ (local only, not in git)
```

---

## Architecture

**Stack:** Streamlit + Supabase (PostgreSQL + Storage) + Railway

**Navigation:** `st.session_state.current_page` router in `app.py`

**Database:** Supabase project at `https://wbdfuvxlkfbaekqnnuma.supabase.co`

**Database Tables:**
- `jobs` — id, its_id, job_name, builder, client_name, responsible_pm, stage, install_type, install_date, installer_crew, install_status, source, notes, created_at
- `tasks` — id, job_id, title, task_type, assigned_to, waiting_on, status, priority, created_at, completed_at
- `photos` — id, job_id, task_id (nullable), file_url, filename, notes, uploaded_at
- `task_templates` — id, template_name, task_type, title, assigned_to, sort_order

**Task Aging:**
- 0–2 days: normal (no indicator)
- 3–5 days: 🟡 yellow
- 6+ days: 🔴 red
- Critical priority → always 🔴
- Urgent priority → 🟡 (or 🔴 if age ≥ 3)

---

## Setup Steps (First-Time)

### 1. Supabase Tables
Run `setup_db.sql` in Supabase → SQL Editor → New Query.

### 2. Supabase Storage Bucket
In Supabase Dashboard → Storage → New Bucket:
- Name: `job-photos`
- Public: **YES** (enables direct photo URLs without auth)

### 3. Seed Task Templates
Run the app → Settings → "Seed Default Templates" button.

### 4. Install Dependencies
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Run Locally
```bash
streamlit run app.py
```
Or double-click `START.bat`.

### 6. Deploy to Railway
1. Push this repo to a GitHub repo named `pocket-pm`
2. In Railway: connect the GitHub repo
3. Add env vars in Railway dashboard:
   - `SUPABASE_URL=https://wbdfuvxlkfbaekqnnuma.supabase.co`
   - `SUPABASE_KEY=<secret key from .env>`
4. Railway auto-deploys on each git push

---

## Key Design Decisions

1. **Jobs are cards, tasks attach to jobs** — not the other way around
2. **No separate install_schedule table** — install calendar filters `jobs` by `install_date`
3. **Assigned To ≠ Responsible PM** — Karl stays accountable even when delegated
4. **task_id on photos is nullable** — job-level site photos supported without a task
5. **Single user (Karl) to start** — no auth layer needed; add Streamlit-Authenticator later if multi-user is needed
6. **Source field on jobs** — `manual` (created in Pocket PM) or `intake` (pushed from intake-to-spec)

---

## Remaining / Future Work

### P1 — First Launch Bugs (test immediately)
- [ ] Verify Supabase key format works with supabase-py 2.x (`sb_secret_` format vs old JWT)
- [ ] Test photo upload + Supabase Storage public URL
- [ ] Mobile browser test: check layout on iPhone Safari

### P2 — UX Polish
- [ ] Add completed task toggle (show/hide) on Job Detail page
- [ ] Add bulk-complete checkbox on Task Queue → My Tasks tab
- [ ] Add task edit form (title, type, priority) on Job Detail
- [ ] Mobile-optimized CSS overrides (larger tap targets, stacked columns on small screens)
- [ ] Add "jump to job" link on task rows in Task Queue

### P3 — intake-to-spec Bridge
In `intake-to-spec/app.py`, after successful job creation, add a button:
```python
if st.button("Push to Pocket PM"):
    import requests
    # POST to Supabase REST API
    requests.post(
        "https://wbdfuvxlkfbaekqnnuma.supabase.co/rest/v1/jobs",
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
        json={"job_name": job.job_name, "its_id": job.job_id, "source": "intake", ...}
    )
```

### P4 — Multi-PM Support (future)
- Add Streamlit-Authenticator for login
- Replace hardcoded `"Karl"` with `st.session_state.username`
- Add PM filter to Jobs kanban

### P5 — Spec Builder Integration (future)
- When spec selections made in intake-to-spec (floating vanity, appliance panels, etc.)
  auto-generate additional tasks in Pocket PM via the same REST API bridge

---

## Known Issues / Watch Out For

1. **Supabase key format:** The new `sb_secret_` format was introduced in 2025. Make sure
   `supabase-py >= 2.0.0` is installed. If auth fails, check Supabase dashboard for the classic JWT key.

2. **Photo MIME types on HEIC:** iOS HEIC photos may need conversion before upload. Add
   `Pillow` to requirements and convert HEIC → JPEG if upload fails.

3. **Streamlit on mobile:** Columns collapse poorly on small screens. For critical mobile paths
   (quick add, mark complete), ensure single-column fallback exists.

4. **Railway SQLite caveat:** This app uses Supabase (cloud Postgres), NOT SQLite. No persistent
   volume needed on Railway. Do not add SQLite to this project.

---

## File Reference

| File | Purpose |
|------|---------|
| `app.py` | Nav bar + page router |
| `core/constants.py` | All lists: STAGES, ROLES, TASK_TYPES, etc. |
| `core/supabase_client.py` | Singleton `get_client()` → Supabase Client |
| `core/jobs.py` | `get_all_jobs`, `create_job`, `update_job_stage`, `get_install_jobs` |
| `core/tasks.py` | `get_my_tasks`, `create_task`, `complete_task`, `get_age_indicator` |
| `core/photos.py` | `upload_photo` → Supabase Storage |
| `core/templates.py` | `seed_templates`, `get_template_tasks` |
| `pages/home.py` | Dashboard with quick-add + My Tasks + Waiting + Installs |
| `pages/jobs_kanban.py` | 6-column Kanban + new job form |
| `pages/job_detail.py` | Full job view: tasks by type, delegate, photos |
| `pages/task_queue.py` | My/Team/Waiting tabs |
| `pages/install_calendar.py` | Weekly calendar grid |
| `pages/settings.py` | Template seeder, connection test |
| `setup_db.sql` | Run once in Supabase SQL editor |
| `Procfile` | Railway start command |
