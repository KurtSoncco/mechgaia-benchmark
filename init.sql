-- Database initialization script for MechGAIA
-- This script sets up the PostgreSQL database schema

-- Create the main database if it doesn't exist
-- (This is handled by the POSTGRES_DB environment variable)

-- Create evaluations table
CREATE TABLE IF NOT EXISTS evaluations (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    task_level INTEGER NOT NULL,
    task_id VARCHAR(255) NOT NULL,
    final_score DECIMAL(10, 6) NOT NULL,
    details JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    submission_data JSONB NOT NULL,
    evaluation_time_ms INTEGER NOT NULL,
    platform VARCHAR(50) DEFAULT 'AgentBeats',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create leaderboard table
CREATE TABLE IF NOT EXISTS leaderboard (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) UNIQUE NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    total_score DECIMAL(10, 6) NOT NULL,
    evaluations_count INTEGER NOT NULL,
    best_score DECIMAL(10, 6) NOT NULL,
    last_evaluation TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_evaluations_agent_id ON evaluations(agent_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_task_level ON evaluations(task_level);
CREATE INDEX IF NOT EXISTS idx_evaluations_timestamp ON evaluations(timestamp);
CREATE INDEX IF NOT EXISTS idx_evaluations_platform ON evaluations(platform);

CREATE INDEX IF NOT EXISTS idx_leaderboard_total_score ON leaderboard(total_score DESC);
CREATE INDEX IF NOT EXISTS idx_leaderboard_best_score ON leaderboard(best_score DESC);
CREATE INDEX IF NOT EXISTS idx_leaderboard_evaluations_count ON leaderboard(evaluations_count DESC);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_leaderboard_updated_at 
    BEFORE UPDATE ON leaderboard 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for testing
INSERT INTO evaluations (agent_id, agent_name, task_level, task_id, final_score, details, timestamp, submission_data, evaluation_time_ms, platform)
VALUES 
    ('sample_agent_1', 'Sample Agent 1', 1, 'mechgaia_level_1', 1.0, '{"numerical_accuracy": 1.0, "code_executes": 1.0}', NOW(), '{"answer_pa": 31830000}', 150, 'AgentBeats'),
    ('sample_agent_1', 'Sample Agent 1', 2, 'mechgaia_level_2', 0.8, '{"valid_material_choice": 1.0, "constraint_satisfied": 0.6}', NOW(), '{"chosen_material": "Steel_1020"}', 200, 'AgentBeats'),
    ('sample_agent_2', 'Sample Agent 2', 1, 'mechgaia_level_1', 0.9, '{"numerical_accuracy": 0.9, "code_executes": 1.0}', NOW(), '{"answer_pa": 30000000}', 180, 'AgentBeats')
ON CONFLICT DO NOTHING;

-- Update leaderboard with sample data
INSERT INTO leaderboard (agent_id, agent_name, total_score, evaluations_count, best_score, last_evaluation)
SELECT 
    agent_id,
    agent_name,
    SUM(final_score) as total_score,
    COUNT(*) as evaluations_count,
    MAX(final_score) as best_score,
    MAX(timestamp) as last_evaluation
FROM evaluations
GROUP BY agent_id, agent_name
ON CONFLICT (agent_id) DO UPDATE SET
    total_score = EXCLUDED.total_score,
    evaluations_count = EXCLUDED.evaluations_count,
    best_score = EXCLUDED.best_score,
    last_evaluation = EXCLUDED.last_evaluation,
    updated_at = NOW();
