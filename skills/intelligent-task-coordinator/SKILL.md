---
name: intelligent-task-coordinator
description: Intelligent task decomposition and agent orchestration. Automatically analyzes complex tasks, breaks them into subtasks, discovers and selects appropriate skills and AI agents based on task requirements, coordinates execution, and aggregates results. Use when facing multi-step complex tasks that require coordination of multiple specialized agents.
---

# Intelligent Task Coordinator

## Overview

This skill provides **intelligent task decomposition** and **dynamic agent orchestration**. It analyzes complex tasks, breaks them down into manageable subtasks, discovers available skills and agents, matches them to subtasks based on capabilities, coordinates execution, and aggregates results.

## Key Features

- **Automatic Task Decomposition** - Break complex tasks into logical subtasks
- **Skill Discovery** - Scan available skills and match to task requirements
- **Agent Selection** - Choose optimal agents based on capabilities and availability
- **Dynamic Orchestration** - Adapt workflow based on execution results
- **Result Aggregation** - Combine results from multiple agents into coherent output

## Architecture

```
┌─────────────────┐
│  User Request   │
│  "Analyze global│
│   assets and    │
│   create report"│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Intelligent Task Coordinator   │
│  1. Analyze task intent         │
│  2. Decompose into subtasks     │
│  3. Discover skills & agents    │
│  4. Match & assign              │
│  5. Coordinate execution        │
│  6. Aggregate results           │
└────────┬────────────────────────┘
         │
         ├──────────────┬──────────────┬──────────────┬──────────────┐
         ▼              ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Skill:      │ │ Skill:      │ │ Skill:      │ │ Skill:      │ │ Skill:      │
│ stock-      │ │ yahoo-      │ │ plotly      │ │ python-     │ │ browser-    │
│ analysis    │ │ finance     │ │             │ │ project     │ │ use         │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Agent:      │ │ Agent:      │ │ Agent:      │ │ Agent:      │ │ Agent:      │
│ Data        │ │ Analysis    │ │ Chart       │ │ Code        │ │ Research    │
│ Fetcher     │ │ Specialist  │ │ Generator   │ │ Executor    │ │ Assistant   │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
         │              │              │              │              │
         └──────────────┴──────────────┴──────────────┴──────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Result         │
                    │  Aggregator     │
                    │  & Reporter     │
                    └─────────────────┘
```

## Core Components

### 1. Task Analyzer

```python
class TaskAnalyzer:
    """Analyze task complexity and requirements"""
    
    def analyze(self, task_description: str) -> TaskAnalysis:
        """
        Analyze task and return:
        - Complexity score (1-10)
        - Required capabilities
        - Estimated subtasks
        - Dependencies
        """
        
        # Extract keywords and intent
        keywords = self.extract_keywords(task_description)
        intent = self.classify_intent(task_description)
        
        # Determine complexity
        complexity = self.estimate_complexity(task_description)
        
        # Identify required capabilities
        capabilities = self.identify_capabilities(keywords, intent)
        
        return TaskAnalysis(
            original_task=task_description,
            complexity=complexity,
            intent=intent,
            required_capabilities=capabilities,
            estimated_subtasks=self.suggest_subtasks(intent, capabilities)
        )
```

### 2. Skill Discovery Engine

```python
class SkillDiscoveryEngine:
    """Discover and catalog available skills"""
    
    def __init__(self):
        self.skills_dir = Path.home() / '.openclaw' / 'workspace' / 'skills'
        self.skill_registry = {}
    
    def scan_skills(self) -> Dict[str, SkillInfo]:
        """Scan workspace for available skills"""
        
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_md = skill_dir / 'SKILL.md'
            if not skill_md.exists():
                continue
            
            # Parse skill metadata
            skill_info = self.parse_skill(skill_md)
            self.skill_registry[skill_info.name] = skill_info
        
        return self.skill_registry
    
    def match_skills_to_task(self, task_requirements: List[str]) -> List[SkillMatch]:
        """Match skills to task requirements"""
        
        matches = []
        for skill_name, skill_info in self.skill_registry.items():
            score = self.calculate_match_score(skill_info, task_requirements)
            if score > 0.5:  # Threshold
                matches.append(SkillMatch(
                    skill=skill_info,
                    confidence=score,
                    matched_capabilities=self.find_matches(skill_info, task_requirements)
                ))
        
        return sorted(matches, key=lambda m: m.confidence, reverse=True)
```

### 3. Agent Selector

```python
class AgentSelector:
    """Select optimal agents for subtasks"""
    
    def __init__(self):
        self.agent_pool = []
        self.session_history = []
    
    def discover_agents(self) -> List[AgentInfo]:
        """Discover available agents (sessions_spawn, existing sessions)"""
        
        # Check active sessions
        sessions = sessions_list(activeMinutes=60)
        
        # Check available agent IDs
        agent_ids = agents_list()
        
        # Build agent pool
        for session in sessions:
            agent_info = AgentInfo(
                id=session['sessionKey'],
                type='session',
                capabilities=session.get('capabilities', []),
                status='busy' if session.get('active') else 'available',
                load=self.estimate_load(session)
            )
            self.agent_pool.append(agent_info)
        
        return self.agent_pool
    
    def select_agent(self, subtask: Subtask) -> AgentSelection:
        """Select best agent for subtask"""
        
        candidates = []
        for agent in self.agent_pool:
            if agent.status != 'available':
                continue
            
            # Calculate fit score
            fit_score = self.calculate_fit(agent, subtask)
            
            # Check capacity
            if agent.load > 0.8:
                continue
            
            candidates.append((agent, fit_score))
        
        if not candidates:
            # Spawn new agent if needed
            return self.spawn_agent_for_task(subtask)
        
        # Select best candidate
        best_agent, best_score = max(candidates, key=lambda x: x[1])
        
        return AgentSelection(
            agent=best_agent,
            confidence=best_score,
            strategy='reuse_existing'
        )
```

### 4. Task Decomposer

```python
class TaskDecomposer:
    """Decompose complex tasks into subtasks"""
    
    DECOMPOSITION_PATTERNS = {
        'data_analysis': [
            'fetch_data',
            'clean_data',
            'analyze_data',
            'visualize_results',
            'generate_report'
        ],
        'research': [
            'define_research_question',
            'search_sources',
            'extract_information',
            'synthesize_findings',
            'write_report'
        ],
        'development': [
            'understand_requirements',
            'design_solution',
            'implement_code',
            'test_implementation',
            'document_solution'
        ],
        'asset_analysis': [
            'fetch_historical_data',
            'calculate_technical_indicators',
            'perform_fundamental_analysis',
            'generate_price_predictions',
            'create_visualizations',
            'compile_investment_recommendations'
        ]
    }
    
    def decompose(self, task_analysis: TaskAnalysis) -> List[Subtask]:
        """Decompose task into subtasks"""
        
        # Select decomposition pattern
        pattern = self.select_pattern(task_analysis.intent)
        
        subtasks = []
        for i, step in enumerate(pattern):
            subtask = Subtask(
                id=f"subtask_{i+1}",
                description=self.generate_description(step, task_analysis),
                required_capabilities=self.get_required_capabilities(step),
                dependencies=[f"subtask_{i}"] if i > 0 else [],
                estimated_duration=self.estimate_duration(step),
                priority=self.calculate_priority(step, pattern)
            )
            subtasks.append(subtask)
        
        return subtasks
```

### 5. Workflow Orchestrator

```python
class WorkflowOrchestrator:
    """Orchestrate execution of subtasks across agents"""
    
    def __init__(self):
        self.execution_graph = nx.DiGraph()
        self.results = {}
    
    def build_execution_graph(self, subtasks: List[Subtask]) -> nx.DiGraph:
        """Build DAG of task dependencies"""
        
        for subtask in subtasks:
            self.execution_graph.add_node(
                subtask.id,
                subtask=subtask,
                status='pending'
            )
            
            for dep in subtask.dependencies:
                self.execution_graph.add_edge(dep, subtask.id)
        
        return self.execution_graph
    
    async def execute(self) -> ExecutionResult:
        """Execute workflow with parallel execution where possible"""
        
        # Find ready tasks (no pending dependencies)
        ready_tasks = self.get_ready_tasks()
        
        while ready_tasks:
            # Execute ready tasks in parallel
            tasks = [
                self.execute_subtask(task_id)
                for task_id in ready_tasks
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update graph
            for task_id, result in zip(ready_tasks, results):
                self.execution_graph.nodes[task_id]['status'] = 'completed'
                self.execution_graph.nodes[task_id]['result'] = result
                self.results[task_id] = result
            
            # Find next ready tasks
            ready_tasks = self.get_ready_tasks()
        
        return ExecutionResult(
            success=True,
            results=self.results,
            execution_time=self.calculate_execution_time()
        )
```

## Usage Examples

### Example 1: Global Asset Analysis

```python
# User request
task = "Analyze 7 major asset classes (Bitcoin, Gold, Silver, Oil, Copper, Lithium, DRAM) 
        with 20-year historical data, technical indicators, price predictions for 1M/3M/6M/1Y/2Y/5Y, 
        and generate interactive charts with investment recommendations"

# Coordinator automatically:
# 1. Analyzes task complexity → Score: 8/10
# 2. Decomposes into subtasks:
#    - Fetch historical data for 7 assets
#    - Calculate technical indicators (RSI, MACD, Bollinger)
#    - Run Monte Carlo simulations for predictions
#    - Generate interactive charts
#    - Compile investment recommendations
# 3. Discovers matching skills:
#    - stock-analysis
#    - yahoo-finance
#    - plotly
#    - python-project
# 4. Selects agents:
#    - Data fetching agent (existing session)
#    - Analysis agent (sessions_spawn)
#    - Chart generation agent (sessions_spawn)
#    - Report writing agent (existing session)
# 5. Executes workflow and aggregates results
```

### Example 2: Research Report

```python
task = "Research the impact of AI on semiconductor industry, 
        find top 10 companies, analyze their financials, 
        and create investment ranking"

# Automatic decomposition:
# 1. Search for AI semiconductor companies
# 2. Filter top 10 by market cap
# 3. Fetch financial data for each
# 4. Calculate valuation metrics
# 5. Rank by investment attractiveness
# 6. Generate report

# Skills matched:
# - web_search (for company research)
# - yahoo-finance (for financial data)
# - stock-analysis (for valuation)
# - python-project (for ranking algorithm)
```

## Implementation

### Main Coordinator Class

```python
class IntelligentTaskCoordinator:
    """Main coordinator that ties everything together"""
    
    def __init__(self):
        self.analyzer = TaskAnalyzer()
        self.decomposer = TaskDecomposer()
        self.skill_discovery = SkillDiscoveryEngine()
        self.agent_selector = AgentSelector()
        self.orchestrator = WorkflowOrchestrator()
        
        # Initialize
        self.skill_discovery.scan_skills()
        self.agent_selector.discover_agents()
    
    async def execute_task(self, task_description: str) -> CoordinatorResult:
        """Execute a complex task with automatic decomposition and orchestration"""
        
        # Step 1: Analyze task
        print(f"📊 Analyzing task: {task_description[:100]}...")
        task_analysis = self.analyzer.analyze(task_description)
        
        # Step 2: Decompose into subtasks
        print(f"🔧 Decomposing into {len(task_analysis.estimated_subtasks)} subtasks...")
        subtasks = self.decomposer.decompose(task_analysis)
        
        # Step 3: Discover and match skills
        print("🔍 Discovering relevant skills...")
        skill_matches = self.skill_discovery.match_skills_to_task(
            task_analysis.required_capabilities
        )
        
        # Step 4: Select agents for each subtask
        print("🤖 Selecting optimal agents...")
        agent_assignments = []
        for subtask in subtasks:
            selection = self.agent_selector.select_agent(subtask)
            agent_assignments.append((subtask, selection))
        
        # Step 5: Build execution graph
        print("📋 Building execution workflow...")
        self.orchestrator.build_execution_graph(subtasks)
        
        # Step 6: Execute workflow
        print("⚡ Executing workflow...")
        execution_result = await self.orchestrator.execute()
        
        # Step 7: Aggregate results
        print("📦 Aggregating results...")
        final_result = self.aggregate_results(execution_result.results)
        
        return CoordinatorResult(
            success=execution_result.success,
            task_analysis=task_analysis,
            subtasks=subtasks,
            skill_matches=skill_matches,
            agent_assignments=agent_assignments,
            execution_result=execution_result,
            final_result=final_result
        )
    
    def aggregate_results(self, results: Dict[str, Any]) -> Any:
        """Aggregate results from multiple agents into coherent output"""
        
        # Combine data from all subtasks
        combined = {
            'summary': self.generate_summary(results),
            'details': results,
            'recommendations': self.generate_recommendations(results),
            'visualizations': self.collect_visualizations(results),
            'metadata': {
                'total_subtasks': len(results),
                'successful': sum(1 for r in results.values() if not isinstance(r, Exception)),
                'failed': sum(1 for r in results.values() if isinstance(r, Exception))
            }
        }
        
        return combined
```

### Integration with OpenClaw

```python
# Using sessions_spawn for dynamic agent creation
async def spawn_agent_for_subtask(self, subtask: Subtask) -> AgentInfo:
    """Spawn new agent for subtask if no existing agent available"""
    
    # Determine required model based on task type
    if 'analysis' in subtask.required_capabilities:
        model = 'bailian/qwen3.5-plus'
    elif 'chart' in subtask.required_capabilities:
        model = 'bailian/qwen3.5-plus'  # Good at code generation
    else:
        model = 'default'
    
    # Spawn agent
    result = await sessions_spawn(
        task=subtask.description,
        model=model,
        timeoutSeconds=subtask.estimated_duration * 60,
        cleanup='delete'
    )
    
    return AgentInfo(
        id=result['sessionKey'],
        type='spawned',
        capabilities=subtask.required_capabilities,
        status='running',
        load=0.5
    )

# Using message for inter-agent communication
async def send_task_to_agent(self, agent_id: str, task: Subtask):
    """Send task to specific agent session"""
    
    await sessions_send(
        sessionKey=agent_id,
        message=json.dumps({
            'type': 'task_assignment',
            'task_id': task.id,
            'description': task.description,
            'requirements': task.required_capabilities,
            'deadline': task.estimated_duration
        })
    )
```

## Skill Matching Algorithm

```python
def calculate_match_score(self, skill: SkillInfo, requirements: List[str]) -> float:
    """Calculate how well a skill matches task requirements"""
    
    score = 0.0
    matches = []
    
    # Check name match
    for req in requirements:
        if req.lower() in skill.name.lower():
            score += 0.3
            matches.append(('name', req))
    
    # Check description match
    if skill.description:
        for req in requirements:
            if req.lower() in skill.description.lower():
                score += 0.2
                matches.append(('description', req))
    
    # Check capabilities
    if hasattr(skill, 'capabilities'):
        for req in requirements:
            for cap in skill.capabilities:
                if req.lower() in cap.lower():
                    score += 0.25
                    matches.append(('capability', req))
    
    # Check tools mentioned
    if hasattr(skill, 'tools'):
        for req in requirements:
            for tool in skill.tools:
                if req.lower() in tool.lower():
                    score += 0.15
                    matches.append(('tool', req))
    
    return min(score, 1.0)  # Cap at 1.0
```

## Monitoring and Debugging

```python
class WorkflowMonitor:
    """Monitor workflow execution and provide insights"""
    
    def __init__(self):
        self.events = []
        self.metrics = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'avg_execution_time': 0,
            'skills_used': set(),
            'agents_used': set()
        }
    
    def log_event(self, event_type: str, details: Dict):
        """Log workflow event"""
        self.events.append({
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'details': details
        })
    
    def generate_report(self) -> str:
        """Generate execution report"""
        report = f"""
# Workflow Execution Report

## Summary
- Total Tasks: {self.metrics['total_tasks']}
- Completed: {self.metrics['completed_tasks']}
- Failed: {self.metrics['failed_tasks']}
- Success Rate: {self.metrics['completed_tasks'] / max(self.metrics['total_tasks'], 1) * 100:.1f}%
- Avg Execution Time: {self.metrics['avg_execution_time']:.2f}s

## Skills Used
{', '.join(self.metrics['skills_used']) or 'None'}

## Agents Used
{', '.join(self.metrics['agents_used']) or 'None'}

## Timeline
"""
        for event in self.events:
            report += f"- [{event['timestamp']}] {event['type']}: {event['details']}\n"
        
        return report
```

## Quick Start

```python
# Initialize coordinator
coordinator = IntelligentTaskCoordinator()

# Execute complex task
result = await coordinator.execute_task(
    "Analyze global asset classes with historical data, "
    "technical indicators, price predictions, and generate "
    "interactive charts with investment recommendations"
)

# Review results
print(f"✅ Task completed: {result.success}")
print(f"📊 Subtasks executed: {len(result.subtasks)}")
print(f"🛠️  Skills used: {[m.skill.name for m in result.skill_matches]}")
print(f"🤖 Agents involved: {len(result.agent_assignments)}")
```

---

**This skill automatically decomposes complex tasks, discovers relevant skills and agents, and orchestrates their execution!** 🚀
