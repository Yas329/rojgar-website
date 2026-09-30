# LatestRojgar live admin setup

This branch adds a database-backed admin panel for the existing static Vercel website.

## 1. Create a Supabase project

Create a Supabase project, open **SQL Editor**, and run the complete contents of:

`supabase-schema.sql`

## 2. Add Vercel environment variables

In Vercel -> Project -> Settings -> Environment Variables add:

- `SUPABASE_URL` = your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` = your Supabase service-role key
- `ADMIN_API_TOKEN` = a long random private token/password you create

Add them to Production and Preview environments, then redeploy.

Important: never paste the Supabase service-role key into HTML, client JavaScript, or GitHub source code. It stays only in Vercel environment variables.

## 3. Use the admin panel

Open:

`https://latestrojgar.in/admin.html`

Enter the same value you configured as `ADMIN_API_TOKEN`.

The admin panel supports:
- create jobs
- publish or save drafts
- edit jobs
- delete jobs
- SEO title, description and slug
- dates, fees, age limits and eligibility
- application/notification/official links

## 4. Public pages

Published jobs are loaded automatically by:

- `/latest-jobs.html`
- `/jobs/<slug>`

The Vercel rewrite in `vercel.json` maps clean job URLs to `job.html`.

## Security

The browser never receives the Supabase service-role key. Database writes go through `/api/jobs` on Vercel.

This first version uses one private admin token. If multiple writers are added later, replace it with Supabase Auth and individual admin accounts.
