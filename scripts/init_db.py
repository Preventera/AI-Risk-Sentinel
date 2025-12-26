#!/usr/bin/env python
"""
Database Initialization Script
==============================

Creates database tables and initial schema for AI Risk Sentinel.

Usage:
    python scripts/init_db.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# Load environment variables
load_dotenv()

console = Console()


# SQL for creating tables
INIT_SQL = """
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enum types
DO $$ BEGIN
    CREATE TYPE risk_source AS ENUM (
        'hf_catalog', 'mit_repository', 'ai_incident_db', 'internal', 'regulatory'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE mit_category AS ENUM (
        'discrimination_toxicity', 'ai_system_safety', 'misinformation',
        'malicious_actors', 'privacy_security', 'human_computer_interaction',
        'socioeconomic_environmental'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE severity_level AS ENUM ('1', '2', '3', '4', '5');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE validation_status AS ENUM ('pending', 'validated', 'rejected');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Main risks table
CREATE TABLE IF NOT EXISTS risks (
    risk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source risk_source NOT NULL,
    source_id VARCHAR(500),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    model_type VARCHAR(100),
    modality_input VARCHAR(50),
    modality_output VARCHAR(50),
    mit_category mit_category NOT NULL,
    mit_subcategory VARCHAR(100),
    deepmind_category VARCHAR(100),
    context_layer VARCHAR(50),
    sst_relevance_score FLOAT DEFAULT 0.0 CHECK (sst_relevance_score >= 0 AND sst_relevance_score <= 1),
    sst_categories TEXT[],
    severity_potential INTEGER DEFAULT 3 CHECK (severity_potential >= 1 AND severity_potential <= 5),
    likelihood_estimate FLOAT CHECK (likelihood_estimate >= 0 AND likelihood_estimate <= 1),
    mitigation_exists BOOLEAN DEFAULT FALSE,
    mitigation_description TEXT,
    evidence_sources TEXT[],
    incident_ids TEXT[],
    embedding vector(1024),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    validated_by VARCHAR(100),
    validation_status validation_status DEFAULT 'pending',
    CONSTRAINT title_min_length CHECK (char_length(title) >= 5)
);

-- Incidents table (from AI Incident Database)
CREATE TABLE IF NOT EXISTS incidents (
    incident_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(100) UNIQUE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    date_occurred DATE,
    date_reported DATE,
    source_url TEXT,
    mit_category mit_category,
    severity INTEGER CHECK (severity >= 1 AND severity <= 5),
    harm_type VARCHAR(100),
    affected_parties TEXT[],
    ai_system_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Model cards table (from Hugging Face)
CREATE TABLE IF NOT EXISTS model_cards (
    model_id VARCHAR(500) PRIMARY KEY,
    model_name VARCHAR(500),
    author VARCHAR(200),
    model_type VARCHAR(100),
    has_risk_section BOOLEAN DEFAULT FALSE,
    risk_section_text TEXT,
    tags TEXT[],
    downloads INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    last_modified TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Metrics snapshots table
CREATE TABLE IF NOT EXISTS metrics_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_date DATE NOT NULL,
    global_bsi FLOAT NOT NULL,
    documentation_quality_score FLOAT,
    total_risks INTEGER,
    total_incidents INTEGER,
    model_cards_analyzed INTEGER,
    category_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    user_id VARCHAR(100),
    old_value JSONB,
    new_value JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Agent runs table
CREATE TABLE IF NOT EXISTS agent_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(100) NOT NULL,
    agent_level INTEGER CHECK (agent_level >= 1 AND agent_level <= 5),
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    items_processed INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_risks_source ON risks(source);
CREATE INDEX IF NOT EXISTS idx_risks_mit_category ON risks(mit_category);
CREATE INDEX IF NOT EXISTS idx_risks_validation ON risks(validation_status);
CREATE INDEX IF NOT EXISTS idx_risks_created ON risks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_risks_sst_relevance ON risks(sst_relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_risks_embedding ON risks USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_incidents_category ON incidents(mit_category);
CREATE INDEX IF NOT EXISTS idx_incidents_date ON incidents(date_occurred DESC);

CREATE INDEX IF NOT EXISTS idx_model_cards_type ON model_cards(model_type);
CREATE INDEX IF NOT EXISTS idx_model_cards_has_risks ON model_cards(has_risk_section);

CREATE INDEX IF NOT EXISTS idx_metrics_date ON metrics_snapshots(snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_name ON agent_runs(agent_name, started_at DESC);

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_risks_updated_at ON risks;
CREATE TRIGGER update_risks_updated_at
    BEFORE UPDATE ON risks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_incidents_updated_at ON incidents;
CREATE TRIGGER update_incidents_updated_at
    BEFORE UPDATE ON incidents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_model_cards_updated_at ON model_cards;
CREATE TRIGGER update_model_cards_updated_at
    BEFORE UPDATE ON model_cards
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust user as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ars_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ars_user;
"""


async def init_database():
    """Initialize the database with required schema."""
    import asyncpg
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Construct from individual variables
        user = os.getenv("POSTGRES_USER", "ars_user")
        password = os.getenv("POSTGRES_PASSWORD", "ars_password")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "ai_risk_sentinel")
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    
    # Remove asyncpg prefix if present
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    console.print(Panel(
        f"[bold]Database URL:[/bold] {database_url.split('@')[1] if '@' in database_url else database_url}",
        title="🔧 Database Configuration",
        border_style="blue"
    ))
    
    try:
        console.print("[yellow]Connecting to database...[/yellow]")
        conn = await asyncpg.connect(database_url)
        
        console.print("[yellow]Creating schema...[/yellow]")
        await conn.execute(INIT_SQL)
        
        # Verify tables created
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        
        table_names = [t["tablename"] for t in tables]
        
        console.print(Panel(
            "\n".join([f"✅ {name}" for name in table_names]),
            title="📋 Tables Created",
            border_style="green"
        ))
        
        await conn.close()
        
        console.print("\n[bold green]✅ Database initialization complete![/bold green]")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
        console.print("\n[yellow]Troubleshooting:[/yellow]")
        console.print("1. Ensure PostgreSQL is running (docker-compose up -d db)")
        console.print("2. Check your .env file configuration")
        console.print("3. Verify network connectivity to database host")
        sys.exit(1)


def main():
    console.print(Panel.fit(
        "[bold blue]🛡️ AI Risk Sentinel - Database Initialization[/bold blue]",
        border_style="blue"
    ))
    console.print()
    
    asyncio.run(init_database())


if __name__ == "__main__":
    main()
