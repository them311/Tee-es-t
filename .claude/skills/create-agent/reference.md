# Agent Creation - Reference Guide

## Prompt Engineering Principles

### 1. Be Direct and Specific
```
BAD:  "Help the user with their code"
GOOD: "Review Python code for OWASP Top 10 vulnerabilities. For each issue found, provide the file path, line number, vulnerability type, severity (CRITICAL/HIGH/MEDIUM/LOW), and a concrete fix."
```

### 2. Use XML Tags for Structure
```xml
<role>You are a database optimization expert.</role>
<context>The application uses PostgreSQL 15 with 50M+ rows in the orders table.</context>
<task>Analyze the provided query and suggest index optimizations.</task>
<constraints>
- Do not suggest schema changes
- Optimize for read-heavy workloads
- Consider existing indexes before adding new ones
</constraints>
```

### 3. Few-Shot Examples Are Critical
Always include at least one input/output example. This anchors the agent's behavior more reliably than instructions alone.

```
<example>
<user-input>Review this function: def login(u, p): return u == "admin"</user-input>
<agent-output>
## Security Issues Found

### CRITICAL: Hardcoded Authentication
- **File**: auth.py:1
- **Issue**: Authentication bypasses password verification entirely
- **Fix**: Implement proper password hashing with bcrypt
```python
from bcrypt import checkpw
def login(username, password):
    user = db.get_user(username)
    if not user:
        return False
    return checkpw(password.encode(), user.password_hash)
```
</agent-output>
</example>
```

### 4. Control Autonomy Level

**Proactive Agent** (default for development tasks):
```
By default, implement changes rather than only suggesting them.
If the user's intent is unclear, infer the most useful action and proceed,
using tools to discover any missing details instead of guessing.
```

**Conservative Agent** (for sensitive operations):
```
Do not take action unless explicitly instructed.
When the user's intent is ambiguous, present options and ask for confirmation.
Never modify production systems without explicit approval.
```

## Agent Architecture Patterns

### Pattern 1: Single Specialist Agent
Best for focused, well-defined tasks.
```
User -> [Specialist Agent] -> Output
```

### Pattern 2: Router + Specialists
Best for multi-domain tasks.
```
User -> [Router Agent] -> [Agent A] -> Output
                       -> [Agent B] -> Output
                       -> [Agent C] -> Output
```

### Pattern 3: Pipeline
Best for sequential processing.
```
User -> [Research Agent] -> [Analysis Agent] -> [Implementation Agent] -> Output
```

### Pattern 4: Review Loop
Best for quality-critical tasks.
```
User -> [Implementation Agent] -> [Review Agent] -> Pass? -> Output
                                                  -> Fail? -> [Implementation Agent] (retry)
```

## Tool Annotations

### Read-Only Tools (Safe for Parallel Execution)
- `Read` - Read files
- `Grep` - Search file contents
- `Glob` - Find files by pattern
- `WebSearch` - Search the web
- `WebFetch` - Fetch web content

### Mutating Tools (Run Sequentially)
- `Edit` - Modify files
- `Write` - Create/overwrite files
- `Bash` - Execute commands
- `NotebookEdit` - Edit notebooks

## Error Handling in Custom Tools

Always return structured errors instead of throwing:
```python
# GOOD - Agent can react and retry
return {
    "content": [{"type": "text", "text": "Connection timeout after 30s"}],
    "is_error": True,
}

# BAD - Breaks the agent loop
raise ConnectionError("timeout")
```

## Session Management

- Use `query()` for stateless, one-off tasks
- Use `ClaudeSDKClient` for multi-turn conversations needing context
- Resume sessions with `session_id` for long-running workflows
- Fork sessions for parallel exploration of different approaches

## Common Mistakes

1. **Too many tools** - Agents get confused with 20+ tools. Keep it under 10.
2. **Vague instructions** - "Be helpful" means nothing. Specify exact behaviors.
3. **No examples** - Without examples, output format is unpredictable.
4. **Missing constraints** - Without boundaries, agents hallucinate or go off-topic.
5. **Monolithic prompts** - 1000-line prompts degrade performance. Split into files.
6. **Wrong model** - Using opus for simple tasks wastes time and money.
7. **No error guidance** - Tell the agent what to do when things fail.
