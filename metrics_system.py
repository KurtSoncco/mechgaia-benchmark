"""
MechGAIA Metrics and Leaderboard System

This module handles metrics collection, storage, and leaderboard functionality
for the MechGAIA benchmark platform.
"""

import json
import sqlite3
import redis
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class EvaluationResult:
    """Data class for storing evaluation results."""
    agent_id: str
    agent_name: str
    task_level: int
    task_id: str
    final_score: float
    details: Dict[str, Any]
    timestamp: datetime
    submission_data: Dict[str, Any]
    evaluation_time_ms: int
    platform: str = "AgentBeats"


class MetricsCollector:
    """Collects and stores evaluation metrics."""
    
    def __init__(self, db_path: str = "mechgaia_metrics.db", redis_url: str = "redis://localhost:6379"):
        """
        Initialize the metrics collector.
        
        Args:
            db_path: Path to SQLite database for persistent storage
            redis_url: Redis URL for real-time leaderboard
        """
        self.db_path = db_path
        self.redis_url = redis_url
        self.redis_client = None
        
        try:
            self._init_database()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Warning: Database initialization failed: {e}")
        
        try:
            self._init_redis()
        except Exception as e:
            print(f"Warning: Redis initialization failed: {e}")
    
    def _init_database(self):
        """Initialize SQLite database schema."""
        try:
            # Ensure the directory exists
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
        except Exception as e:
            print(f"Failed to connect to database: {e}")
            raise
        
        # Create evaluations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                task_level INTEGER NOT NULL,
                task_id TEXT NOT NULL,
                final_score REAL NOT NULL,
                details TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                submission_data TEXT NOT NULL,
                evaluation_time_ms INTEGER NOT NULL,
                platform TEXT DEFAULT 'AgentBeats'
            )
        """)
        
        # Create leaderboard table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                total_score REAL NOT NULL,
                evaluations_count INTEGER NOT NULL,
                best_score REAL NOT NULL,
                last_evaluation TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evaluations_agent_id ON evaluations(agent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evaluations_task_level ON evaluations(task_level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evaluations_timestamp ON evaluations(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leaderboard_total_score ON leaderboard(total_score DESC)")
        
        conn.commit()
        conn.close()
    
    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_client.ping()  # Test connection
        except Exception as e:
            print(f"Warning: Redis connection failed: {e}")
            self.redis_client = None
    
    def record_evaluation(self, result: EvaluationResult):
        """
        Record an evaluation result.
        
        Args:
            result: The evaluation result to record
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
        except Exception as e:
            print(f"Failed to connect to database for recording: {e}")
            return
        
        try:
            # Insert evaluation
            cursor.execute("""
                INSERT INTO evaluations 
                (agent_id, agent_name, task_level, task_id, final_score, details, 
                 timestamp, submission_data, evaluation_time_ms, platform)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.agent_id,
                result.agent_name,
                result.task_level,
                result.task_id,
                result.final_score,
                json.dumps(result.details),
                result.timestamp.isoformat(),
                json.dumps(result.submission_data),
                result.evaluation_time_ms,
                result.platform
            ))
            
            # Update leaderboard
            self._update_leaderboard(result)
            
            conn.commit()
            conn.close()
            
            # Update Redis leaderboard
            self._update_redis_leaderboard(result)
        except Exception as e:
            print(f"Failed to record evaluation: {e}")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
    
    def _update_leaderboard(self, result: EvaluationResult):
        """Update the SQLite leaderboard."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current leaderboard entry
        cursor.execute("""
            SELECT total_score, evaluations_count, best_score 
            FROM leaderboard WHERE agent_id = ?
        """, (result.agent_id,))
        
        row = cursor.fetchone()
        
        if row:
            # Update existing entry
            total_score, evaluations_count, best_score = row
            new_total_score = total_score + result.final_score
            new_evaluations_count = evaluations_count + 1
            new_best_score = max(best_score, result.final_score)
            
            cursor.execute("""
                UPDATE leaderboard 
                SET total_score = ?, evaluations_count = ?, best_score = ?,
                    last_evaluation = ?, updated_at = ?
                WHERE agent_id = ?
            """, (
                new_total_score,
                new_evaluations_count,
                new_best_score,
                result.timestamp.isoformat(),
                datetime.now(timezone.utc).isoformat(),
                result.agent_id
            ))
        else:
            # Create new entry
            cursor.execute("""
                INSERT INTO leaderboard 
                (agent_id, agent_name, total_score, evaluations_count, best_score,
                 last_evaluation, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.agent_id,
                result.agent_name,
                result.final_score,
                1,
                result.final_score,
                result.timestamp.isoformat(),
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def _update_redis_leaderboard(self, result: EvaluationResult):
        """Update Redis leaderboard for real-time updates."""
        if not self.redis_client:
            return
        
        try:
            # Update agent's total score
            self.redis_client.zadd(
                "leaderboard:total_score",
                {result.agent_id: result.final_score}
            )
            
            # Update agent's best score
            self.redis_client.zadd(
                "leaderboard:best_score",
                {result.agent_id: result.final_score}
            )
            
            # Update agent info
            agent_info = {
                "agent_name": result.agent_name,
                "last_evaluation": result.timestamp.isoformat(),
                "platform": result.platform
            }
            self.redis_client.hset(f"agent:{result.agent_id}", mapping=agent_info)
            
        except Exception as e:
            print(f"Warning: Redis update failed: {e}")
    
    def get_leaderboard(self, limit: int = 10, sort_by: str = "total_score") -> List[Dict[str, Any]]:
        """
        Get the current leaderboard.
        
        Args:
            limit: Maximum number of entries to return
            sort_by: Sort by 'total_score', 'best_score', or 'evaluations_count'
            
        Returns:
            List of leaderboard entries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        order_by = {
            "total_score": "total_score DESC",
            "best_score": "best_score DESC", 
            "evaluations_count": "evaluations_count DESC"
        }.get(sort_by, "total_score DESC")
        
        cursor.execute(f"""
            SELECT agent_id, agent_name, total_score, evaluations_count, 
                   best_score, last_evaluation, created_at, updated_at
            FROM leaderboard 
            ORDER BY {order_by}
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            entry = dict(zip(columns, row))
            results.append(entry)
        
        conn.close()
        return results
    
    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific agent.
        
        Args:
            agent_id: The agent's unique identifier
            
        Returns:
            Dictionary containing agent statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get leaderboard entry
        cursor.execute("""
            SELECT * FROM leaderboard WHERE agent_id = ?
        """, (agent_id,))
        
        leaderboard_entry = cursor.fetchone()
        
        # Get evaluation history
        cursor.execute("""
            SELECT task_level, final_score, timestamp, evaluation_time_ms
            FROM evaluations 
            WHERE agent_id = ?
            ORDER BY timestamp DESC
        """, (agent_id,))
        
        evaluations = cursor.fetchall()
        
        conn.close()
        
        if not leaderboard_entry:
            return {"error": "Agent not found"}
        
        columns = [desc[0] for desc in cursor.description]
        leaderboard_data = dict(zip(columns, leaderboard_entry))
        
        return {
            "leaderboard": leaderboard_data,
            "evaluations": [
                {
                    "task_level": eval[0],
                    "final_score": eval[1],
                    "timestamp": eval[2],
                    "evaluation_time_ms": eval[3]
                }
                for eval in evaluations
            ]
        }
    
    def get_task_level_stats(self, task_level: int) -> Dict[str, Any]:
        """
        Get statistics for a specific task level.
        
        Args:
            task_level: The task level (1, 2, or 3)
            
        Returns:
            Dictionary containing task level statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_evaluations,
                AVG(final_score) as average_score,
                MAX(final_score) as best_score,
                MIN(final_score) as worst_score,
                COUNT(DISTINCT agent_id) as unique_agents
            FROM evaluations 
            WHERE task_level = ?
        """, (task_level,))
        
        stats = cursor.fetchone()
        
        # Get top performers
        cursor.execute("""
            SELECT agent_id, agent_name, final_score, timestamp
            FROM evaluations 
            WHERE task_level = ?
            ORDER BY final_score DESC
            LIMIT 10
        """, (task_level,))
        
        top_performers = cursor.fetchall()
        
        conn.close()
        
        return {
            "task_level": task_level,
            "total_evaluations": stats[0],
            "average_score": round(stats[1], 3) if stats[1] else 0,
            "best_score": stats[2],
            "worst_score": stats[3],
            "unique_agents": stats[4],
            "top_performers": [
                {
                    "agent_id": perf[0],
                    "agent_name": perf[1],
                    "final_score": perf[2],
                    "timestamp": perf[3]
                }
                for perf in top_performers
            ]
        }


# Global metrics collector instance (lazy initialization)
metrics_collector = None

def get_metrics_collector():
    """Get the global metrics collector instance, creating it if needed."""
    global metrics_collector
    if metrics_collector is None:
        metrics_collector = MetricsCollector()
    return metrics_collector
