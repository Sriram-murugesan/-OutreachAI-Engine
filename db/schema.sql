create table campaigns (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  status text default 'pending',
  created_at timestamp default now()
);

create table leads (
  id uuid default gen_random_uuid() primary key,
  campaign_id uuid references campaigns(id) on delete cascade,
  name text,
  company text,
  linkedin_url text,
  created_at timestamp default now()
);

create table emails (
  id uuid default gen_random_uuid() primary key,
  lead_id uuid references leads(id) on delete cascade,
  persona text,
  email_body text,
  quality_score integer,
  status text default 'generated',
  created_at timestamp default now()
);
alter table leads add column if not exists email text;
alter table emails add column if not exists sent_at timestamp;
alter table emails add column if not exists status text default 'generated';