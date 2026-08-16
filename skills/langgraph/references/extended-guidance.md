<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Collaboration

### Delegation Triggers

- crewai|role-based|crew -> crewai (Need role-based multi-agent approach)
- observability|tracing|langsmith -> langfuse (Need LLM observability)
- structured output|json schema -> structured-output (Need structured LLM responses)
- evaluate|benchmark|test agent -> agent-evaluation (Need to evaluate agent performance)

### Production Agent Stack

Skills: langgraph, langfuse, structured-output

Workflow:

```
1. Design agent graph with LangGraph
2. Add structured outputs for tool responses
3. Integrate Langfuse for observability
4. Test and monitor in production
```

### Multi-Agent System

Skills: langgraph, crewai, agent-communication

Workflow:

```
1. Design agent roles (CrewAI patterns)
2. Implement as LangGraph with subgraphs
3. Add inter-agent communication
4. Orchestrate with supervisor pattern
```

### Evaluated Agent

Skills: langgraph, agent-evaluation, langfuse

Workflow:

```
1. Build agent with LangGraph
2. Create evaluation suite
3. Monitor with Langfuse
4. Iterate based on metrics
```

## Related Skills

Works well with: `crewai`, `autonomous-agents`, `langfuse`, `structured-output`

## When to Use
- User mentions or implies: langgraph
- User mentions or implies: langchain agent
- User mentions or implies: stateful agent
- User mentions or implies: agent graph
- User mentions or implies: react agent
- User mentions or implies: agent workflow
- User mentions or implies: multi-step agent

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
