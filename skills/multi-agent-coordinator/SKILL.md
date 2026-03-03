---
name: multi-agent-coordinator
description: Coordinate multiple AI agents to work together on complex tasks. Use when you need to break down a large task into subtasks and distribute them across specialized agents, or when you want to implement agent-to-agent communication and workflow orchestration.
---

# Multi-Agent Coordinator Skill

## Overview

This skill enables coordination and orchestration of multiple AI agents working together on complex tasks. It provides workflow management, inter-agent communication, and result aggregation capabilities.

## When to Use

Use this skill when:
- You need to coordinate 2+ AI agents on a single project
- Tasks require specialized agents (data analysis, visualization, report generation, etc.)
- You want to implement agent-to-agent communication patterns
- Building complex workflows that exceed single-agent capabilities
- Need to manage agent task queues and result aggregation

## Architecture

```
┌─────────────┐
│  User       │
│  Request    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Coordinator │ ← Main agent (you)
└──────┬──────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Data     │  │ Analysis │  │ Chart    │  │ Report   │
│ Agent    │  │ Agent    │  │ Agent    │  │ Agent    │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
```

## Core Components

### 1. Task Definition

```python
@dataclass
class Task:
    task_id: str
    task_type: str  # 'data', 'analysis', 'chart', 'report'
    description: str
    input_data: Dict[str, Any]
    assigned_agent: Optional[str] = None
    status: str = 'pending'  # pending, in_progress, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None
```

### 2. Agent Registry

```python
AGENT_CAPABILITIES = {
    'data_agent': {
        'capabilities': ['fetch_market_data', 'fetch_economic_data', 'fetch_news'],
        'tools': ['yfinance', 'news_api', 'fred_api'],
        'output_format': 'pandas.DataFrame'
    },
    'analysis_agent': {
        'capabilities': ['technical_analysis', 'fundamental_analysis', 'sentiment_analysis'],
        'tools': ['pandas', 'numpy', 'ta_lib'],
        'output_format': 'dict'
    },
    'chart_agent': {
        'capabilities': ['generate_charts', 'create_dashboards', 'export_images'],
        'tools': ['plotly', 'matplotlib', 'seaborn'],
        'output_format': 'html_file'
    },
    'report_agent': {
        'capabilities': ['generate_reports', 'summarize_findings', 'create_recommendations'],
        'tools': ['jinja2', 'markdown', 'pdf_generator'],
        'output_format': 'markdown'
    }
}
```

### 3. Workflow Engine

```python
class WorkflowEngine:
    def __init__(self):
        self.tasks = []
        self.agents = {}
        self.results = {}
    
    def define_workflow(self, workflow_steps: List[Dict]) -> str:
        """Define a workflow with multiple steps"""
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        for step in workflow_steps:
            task = Task(
                task_id=f"{workflow_id}_{step['id']}",
                task_type=step['type'],
                description=step['description'],
                input_data=step.get('input', {})
            )
            self.tasks.append(task)
        
        return workflow_id
    
    async def execute_workflow(self, workflow_id: str) -> Dict:
        """Execute all tasks in the workflow"""
        for task in self.tasks:
            # Select appropriate agent
            agent = self.select_agent(task.task_type)
            
            # Execute task
            try:
                result = await agent.execute(task)
                task.status = 'completed'
                task.result = result
            except Exception as e:
                task.status = 'failed'
                task.error = str(e)
            
            # Pass result to next task if needed
            self.pass_to_next_task(task)
        
        return self.aggregate_results()
```

## Usage Examples

### Example 1: Global Asset Analysis Workflow

```python
# Define workflow
workflow = [
    {
        'id': 'step1',
        'type': 'data',
        'description': 'Fetch 20-year historical data for 7 asset classes',
        'input': {
            'assets': ['bitcoin', 'gold', 'silver', 'oil', 'copper', 'lithium', 'dram'],
            'period': '20y'
        }
    },
    {
        'id': 'step2',
        'type': 'analysis',
        'description': 'Calculate technical indicators (RSI, MACD, Bollinger Bands)',
        'input': {'indicators': ['rsi', 'macd', 'bollinger', 'volatility']}
    },
    {
        'id': 'step3',
        'type': 'chart',
        'description': 'Generate interactive charts for each asset',
        'input': {'chart_types': ['candlestick', 'rsi', 'macd', 'comparison']}
    },
    {
        'id': 'step4',
        'type': 'report',
        'description': 'Generate comprehensive analysis report',
        'input': {'format': 'html', 'include_predictions': True}
    }
]

# Execute workflow
workflow_id = coordinator.define_workflow(workflow)
results = await coordinator.execute_workflow(workflow_id)
```

### Example 2: Multi-Agent Investment Research

```python
# Parallel execution pattern
tasks = [
    {'agent': 'data_agent', 'task': 'fetch_stock_data', 'symbol': 'AAPL'},
    {'agent': 'data_agent', 'task': 'fetch_stock_data', 'symbol': 'GOOGL'},
    {'agent': 'data_agent', 'task': 'fetch_stock_data', 'symbol': 'MSFT'},
]

# Execute in parallel
results = await asyncio.gather(*[
    agent.execute(task) for task in tasks
])

# Aggregate and analyze
analysis = await analysis_agent.analyze_portfolio(results)
```

## Communication Patterns

### 1. Sequential (Pipeline)

```
Agent1 → Agent2 → Agent3 → Result
```

**Use case:** Data → Analysis → Visualization

### 2. Parallel (Fan-out)

```
        ┌─→ Agent1 ─┐
Root ──┼─→ Agent2 ─┼→ Aggregator → Result
        └─→ Agent3 ─┘
```

**Use case:** Analyze multiple assets simultaneously

### 3. Hierarchical (Tree)

```
        Coordinator
        /    |    \
    Team1  Team2  Team3
     / \    / \    / \
   A1  A2  A3 A4  A5 A6
```

**Use case:** Complex projects with multiple workstreams

## Implementation Guide

### Step 1: Define Agent Roles

```python
ROLES = {
    'coordinator': {
        'responsibilities': ['task_decomposition', 'agent_assignment', 'result_aggregation'],
        'tools': ['sessions_spawn', 'message']
    },
    'specialist': {
        'responsibilities': ['execute_specialized_task', 'report_status'],
        'tools': ['domain_specific_tools']
    }
}
```

### Step 2: Implement Task Queue

```python
import asyncio
from collections import deque

class TaskQueue:
    def __init__(self):
        self.queue = deque()
        self.lock = asyncio.Lock()
    
    async def add_task(self, task: Task):
        async with self.lock:
            self.queue.append(task)
    
    async def get_next_task(self) -> Optional[Task]:
        async with self.lock:
            return self.queue.popleft() if self.queue else None
```

### Step 3: Add Monitoring

```python
class WorkflowMonitor:
    def __init__(self):
        self.metrics = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'avg_execution_time': 0
        }
    
    def update_metrics(self, task: Task, execution_time: float):
        self.metrics['total_tasks'] += 1
        if task.status == 'completed':
            self.metrics['completed_tasks'] += 1
        elif task.status == 'failed':
            self.metrics['failed_tasks'] += 1
        
        # Update average
        n = self.metrics['total_tasks']
        self.metrics['avg_execution_time'] = (
            (self.metrics['avg_execution_time'] * (n-1) + execution_time) / n
        )
```

## Error Handling

### Retry Logic

```python
async def execute_with_retry(agent, task, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await agent.execute(task)
        except Exception as e:
            if attempt == max_retries - 1:
                task.status = 'failed'
                task.error = f"Failed after {max_retries} attempts: {str(e)}"
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Fallback Strategy

```python
FALLBACK_CHAIN = {
    'primary_agent': 'backup_agent_1',
    'backup_agent_1': 'backup_agent_2',
    'backup_agent_2': 'human_review'
}

async def execute_with_fallback(agent, task):
    current_agent = agent
    while current_agent:
        try:
            return await current_agent.execute(task)
        except Exception:
            current_agent = FALLBACK_CHAIN.get(current_agent.name)
    
    raise Exception("All fallback agents failed")
```

## Best Practices

1. **Clear Task Boundaries** - Each agent should have well-defined responsibilities
2. **Idempotent Operations** - Tasks should be safe to retry
3. **Timeout Handling** - Set reasonable timeouts for each task
4. **Progress Tracking** - Report progress after each task completion
5. **Result Validation** - Validate results before passing to next agent
6. **Logging** - Log all inter-agent communications for debugging

## OpenClaw Integration

### Using sessions_spawn

```python
# Spawn sub-agent for specialized task
result = await sessions_spawn(
    task="Analyze technical indicators for BTC-USD using RSI, MACD, and Bollinger Bands",
    agentId="analysis_specialist",
    timeoutSeconds=300
)
```

### Using message tool

```python
# Send task to another agent
await message(
    action="send",
    target="analysis_agent_session",
    message=json.dumps({
        'task': 'technical_analysis',
        'symbol': 'BTC-USD',
        'data': price_data
    })
)
```

## Sample Workflow: Asset Analysis

```python
async def analyze_global_assets():
    # Initialize coordinator
    coordinator = MultiAgentCoordinator()
    
    # Define workflow
    workflow = [
        # Step 1: Fetch data (parallel)
        {'type': 'data', 'assets': ['BTC-USD', 'GC=F', 'SI=F'], 'parallel': True},
        
        # Step 2: Technical analysis (parallel)
        {'type': 'analysis', 'indicators': ['rsi', 'macd', 'bb'], 'parallel': True},
        
        # Step 3: Generate charts (sequential)
        {'type': 'chart', 'chart_types': ['price', 'indicators', 'comparison']},
        
        # Step 4: Generate report (sequential)
        {'type': 'report', 'format': 'html', 'include_forecasts': True}
    ]
    
    # Execute
    workflow_id = coordinator.define_workflow(workflow)
    results = await coordinator.execute_workflow(workflow_id)
    
    return results
```

## Troubleshooting

### Issue: Agent not responding

**Solution:**
1. Check agent status with health check
2. Verify communication channel (queue/API)
3. Increase timeout if task is complex
4. Check logs for errors

### Issue: Results not aggregating

**Solution:**
1. Verify output format matches expected schema
2. Check data serialization (JSON/dict)
3. Ensure all tasks completed before aggregation
4. Add validation step before aggregation

### Issue: Workflow too slow

**Solution:**
1. Identify bottleneck tasks with profiling
2. Convert sequential tasks to parallel where possible
3. Add caching for repeated data fetches
4. Use async/await for I/O operations

## Future Enhancements

1. **Agent Learning** - Agents improve based on feedback
2. **Dynamic Workflow** - Adjust workflow based on intermediate results
3. **Human-in-the-Loop** - Pause for human review at critical points
4. **Agent Marketplace** - Discover and hire specialized agents on-demand
5. **Cost Optimization** - Balance speed vs. cost when selecting agents

---

## Quick Start

```python
# 1. Import the skill
from skills.multi_agent_coordinator import MultiAgentCoordinator

# 2. Initialize
coordinator = MultiAgentCoordinator()

# 3. Define workflow
workflow = [
    {'type': 'data', 'description': 'Fetch market data'},
    {'type': 'analysis', 'description': 'Analyze trends'},
    {'type': 'report', 'description': 'Generate report'}
]

# 4. Execute
workflow_id = coordinator.define_workflow(workflow)
results = await coordinator.execute_workflow(workflow_id)

# 5. Review results
print(f"Workflow completed: {workflow_id}")
print(f"Success rate: {results['success_rate']}")
```

---

**This skill enables you to orchestrate multiple AI agents working together on complex, multi-step tasks!** 🚀
