"""
MechGAIA Leaderboard API

FastAPI-based REST API for accessing MechGAIA benchmark metrics and leaderboard data.
"""

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from metrics_system import EvaluationResult, get_metrics_collector

# Initialize FastAPI app
app = FastAPI(
    title="MechGAIA Leaderboard API",
    description="API for MechGAIA benchmark metrics and leaderboard",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "MechGAIA Leaderboard API",
        "version": "0.1.0",
        "endpoints": {
            "leaderboard": "/leaderboard",
            "agent_stats": "/agent/{agent_id}/stats",
            "task_stats": "/task/{task_level}/stats",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    sort_by: str = Query(
        "total_score", description="Sort by: total_score, best_score, evaluations_count"
    ),
):
    """
    Get the current leaderboard.

    Args:
        limit: Maximum number of entries to return (1-100)
        sort_by: Sort criteria (total_score, best_score, evaluations_count)

    Returns:
        List of leaderboard entries
    """
    try:
        leaderboard = get_metrics_collector().get_leaderboard(limit=limit, sort_by=sort_by)
        return {
            "leaderboard": leaderboard,
            "total_entries": len(leaderboard),
            "sort_by": sort_by,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/{agent_id}/stats")
async def get_agent_stats(agent_id: str):
    """
    Get detailed statistics for a specific agent.

    Args:
        agent_id: The agent's unique identifier

    Returns:
        Agent statistics and evaluation history
    """
    try:
        stats = get_metrics_collector().get_agent_stats(agent_id)
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/task/{task_level}/stats")
async def get_task_stats(task_level: int):
    """
    Get statistics for a specific task level.

    Args:
        task_level: The task level (1, 2, or 3)

    Returns:
        Task level statistics and top performers
    """
    if task_level not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Task level must be 1, 2, or 3")

    try:
        stats = get_metrics_collector().get_task_level_stats(task_level)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluation")
async def record_evaluation(evaluation_data: dict):
    """
    Record a new evaluation result.

    Args:
        evaluation_data: Dictionary containing evaluation result data

    Returns:
        Confirmation of recorded evaluation
    """
    try:
        # Create EvaluationResult object
        result = EvaluationResult(
            agent_id=evaluation_data["agent_id"],
            agent_name=evaluation_data["agent_name"],
            task_level=evaluation_data["task_level"],
            task_id=evaluation_data["task_id"],
            final_score=evaluation_data["final_score"],
            details=evaluation_data["details"],
            timestamp=datetime.now(timezone.utc),
            submission_data=evaluation_data.get("submission_data", {}),
            evaluation_time_ms=evaluation_data.get("evaluation_time_ms", 0),
            platform=evaluation_data.get("platform", "AgentBeats"),
        )

        # Record the evaluation
        get_metrics_collector().record_evaluation(result)

        return {
            "message": "Evaluation recorded successfully",
            "agent_id": result.agent_id,
            "task_level": result.task_level,
            "final_score": result.final_score,
            "timestamp": result.timestamp.isoformat(),
        }

    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required field: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Simple HTML dashboard for viewing leaderboard."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MechGAIA Leaderboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
            .stat-card { background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #007bff; }
            .stat-title { font-weight: bold; color: #495057; margin-bottom: 10px; }
            .stat-value { font-size: 24px; color: #007bff; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f8f9fa; font-weight: bold; }
            .loading { text-align: center; color: #666; }
            .error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0; }
            .refresh-btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 10px 0; }
            .refresh-btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏆 MechGAIA Benchmark Leaderboard</h1>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-title">Total Agents</div>
                    <div class="stat-value" id="total-agents">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Total Evaluations</div>
                    <div class="stat-value" id="total-evaluations">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Best Score</div>
                    <div class="stat-value" id="best-score">-</div>
                </div>
            </div>
            
            <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
            
            <h2>📊 Overall Leaderboard</h2>
            <div id="leaderboard-content" class="loading">Loading leaderboard...</div>
            
            <h2>📈 Task Level Statistics</h2>
            <div id="task-stats-content" class="loading">Loading task statistics...</div>
        </div>

        <script>
            async function loadData() {
                try {
                    // Load leaderboard
                    const leaderboardResponse = await fetch('/leaderboard?limit=20');
                    const leaderboardData = await leaderboardResponse.json();
                    
                    let leaderboardHtml = '<table><tr><th>Rank</th><th>Agent Name</th><th>Total Score</th><th>Evaluations</th><th>Best Score</th><th>Last Evaluation</th></tr>';
                    
                    leaderboardData.leaderboard.forEach((entry, index) => {
                        leaderboardHtml += `
                            <tr>
                                <td>${index + 1}</td>
                                <td>${entry.agent_name}</td>
                                <td>${entry.total_score.toFixed(3)}</td>
                                <td>${entry.evaluations_count}</td>
                                <td>${entry.best_score.toFixed(3)}</td>
                                <td>${new Date(entry.last_evaluation).toLocaleString()}</td>
                            </tr>
                        `;
                    });
                    
                    leaderboardHtml += '</table>';
                    document.getElementById('leaderboard-content').innerHTML = leaderboardHtml;
                    
                    // Update stats
                    document.getElementById('total-agents').textContent = leaderboardData.total_entries;
                    
                    if (leaderboardData.leaderboard.length > 0) {
                        const bestScore = Math.max(...leaderboardData.leaderboard.map(e => e.best_score));
                        document.getElementById('best-score').textContent = bestScore.toFixed(3);
                    }
                    
                    // Load task statistics
                    let taskStatsHtml = '';
                    for (let level = 1; level <= 3; level++) {
                        try {
                            const taskResponse = await fetch(`/task/${level}/stats`);
                            const taskData = await taskResponse.json();
                            
                            taskStatsHtml += `
                                <div class="stat-card">
                                    <div class="stat-title">Level ${level} Statistics</div>
                                    <div>Total Evaluations: ${taskData.total_evaluations}</div>
                                    <div>Average Score: ${taskData.average_score}</div>
                                    <div>Best Score: ${taskData.best_score}</div>
                                    <div>Unique Agents: ${taskData.unique_agents}</div>
                                </div>
                            `;
                        } catch (e) {
                            console.error(`Error loading task ${level} stats:`, e);
                        }
                    }
                    
                    document.getElementById('task-stats-content').innerHTML = taskStatsHtml;
                    
                } catch (error) {
                    document.getElementById('leaderboard-content').innerHTML = `<div class="error">Error loading data: ${error.message}</div>`;
                    document.getElementById('task-stats-content').innerHTML = `<div class="error">Error loading task statistics: ${error.message}</div>`;
                }
            }
            
            // Load data on page load
            loadData();
            
            // Auto-refresh every 30 seconds
            setInterval(loadData, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
