create extension if not exists pgcrypto;

create table if not exists public.jobs (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  slug text not null unique,
  department text,
  advertisement_number text,
  post_name text,
  category text,
  total_posts integer,
  location text,
  application_start date,
  application_end date,
  fee_last_date date,
  correction_date date,
  exam_date text,
  admit_card_date text,
  result_date text,
  general_fee text,
  obc_ews_fee text,
  sc_st_fee text,
  female_fee text,
  payment_method text,
  minimum_age integer,
  maximum_age integer,
  age_relaxation text,
  vacancy_details jsonb not null default '[]'::jsonb,
  qualification text,
  experience text,
  other_conditions text,
  description text,
  apply_url text,
  notification_url text,
  official_url text,
  admit_card_url text,
  result_url text,
  answer_key_url text,
  seo_title text,
  meta_description text,
  keywords text,
  status text not null default 'Draft' check (status in ('Draft','Published')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists jobs_set_updated_at on public.jobs;
create trigger jobs_set_updated_at
before update on public.jobs
for each row execute function public.set_updated_at();

alter table public.jobs enable row level security;