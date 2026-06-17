# ⚡ OutreachAI Engine

An autonomous, multi-agent cold outreach pipeline that takes a list of B2B targets, crawls the web for deep profile research, builds structured psychological personas, drafts hyper-personalized emails, and runs a self-correcting quality control loop before saving or exporting records.

Built with **LangGraph**, **Groq (Llama 3.3 70B)**, **Tavily Search**, **Supabase**, and a premium **Streamlit** control canvas.

---

## 🏗️ Architecture Workflow

The system treats data ingestion and copywriting as a directed cyclic graph (state machine) orchestrated via LangGraph. 

1. **`load_lead`**: Fetches the current lead from the collection state and commits it to Supabase to initialize tracking.
2. **`research`**: Queries the web dynamically via Tavily for current company roles, announcements, and news.
3. **`persona`**: Employs Llama-3.3-70b to summarize the unstructured search artifacts into a refined target profile.
4. **`email_writer`**: Composes a custom cold email tailored explicitly to the generated profile.
5. **`quality_checker`**: Performs self-reflection evaluation on the generated draft. If the score is less than 7 and max retries (up to 2) aren't reached, it forces an edge transition back to `email_writer`.
6. **`save_result`**: Commits finalized drafts and data vectors to Supabase, updating indices to shift to the next contact.

---

## 🛠️ Tech Stack & Infrastructure

* **Orchestration**: LangGraph (State Graph Management)
* **LLM Core Engine**: Groq Cloud AI (`llama-3.3-70b-versatile`)
* **Live Web Context Integration**: Tavily Search API
* **Persistence Layer**: Supabase Database (PostgreSQL)
* **Control Canvas App**: Streamlit (Premium Custom Custom CSS Template Engine)

---

## 📋 Pre-requisites & Database Setup

### 1. Supabase Schema Layout
Ensure your Supabase project contains the tracking relational schemas below. Execute this inside your Supabase SQL Editor:

```sql
-- 1. Campaigns Master Table
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 2. Leads Processing Table
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    company TEXT NOT NULL,
    linkedin_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 3. Emails Generation Log
CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    persona TEXT,
    email_body TEXT,
    quality_score INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);