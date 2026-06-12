# Agent Frameworks Compared — Microsoft Agent Framework vs. LangGraph vs. Semantic Kernel

A practical comparison of the three frameworks used across the *Agentic AI on Azure* course and its
companion projects. All three can build the **same** agent (the IT-helpdesk triage / claims examples in
these repos) — they differ in *how* you express state, tools, and control flow.

> **TL;DR**
> - **Microsoft Agent Framework / Foundry** — Azure-native, **managed hosted agents** + runtime, least ops. Default for this course.
> - **LangGraph** — explicit **graph** of nodes/edges; best when control flow, branching, loops, and human-in-the-loop are first-class.
> - **Semantic Kernel** — lightweight **kernel + plugins**; great for embedding AI skills into existing apps. Now converging into Microsoft Agent Framework 1.0.

---

## At a glance

| | **Microsoft Agent Framework / Foundry** | **LangGraph** | **Semantic Kernel** |
|---|---|---|---|
| Vendor | Microsoft / Azure | LangChain | Microsoft |
| Core abstraction | Hosted **Agent** + tools (Responses API) | **StateGraph** (nodes + edges + state) | **Kernel** + **plugins** (`@kernel_function`) |
| Mental model | "Managed agent I call" | "Explicit state machine I route through" | "AI services + skills I compose" |
| Control flow | Model-driven (tool calls) | **You** define edges/branches/loops | Planner or auto function calling |
| State / memory | Managed threads/conversations | Typed graph **state** (+ checkpointers) | `ChatHistory` / memory connectors |
| Tools | Function tools, MCP, OpenAPI, AI Search, etc. | Any Python fn as a node / tool-calling | `@kernel_function` plugins, OpenAPI, MCP |
| Multi-agent | Built-in orchestration patterns | Graphs/subgraphs, supervisor patterns | Agent group chat / handoffs |
| Hosting | **Managed** (Foundry Agent Service) | You host (it's a library) | You host (it's a library) |
| Azure fit | ★★★ native | ★★ via `langchain-openai` | ★★★ native (`AzureChatCompletion`) |
| Best when | Enterprise Azure, least ops, governance | Complex branching/looping workflows | Embedding skills in an app; .NET + Python |
| In this course | The 12 weekly labs | `agentic-ai-azure-langgraph` | `agentic-ai-azure-semantic-kernel` |

---

## The same idea in each framework

**1. Microsoft Agent Framework / Foundry** — define a hosted agent with a tool; the model decides to call it.
```python
tool = FunctionTool(name="policy_lookup", parameters={...}, description="...", strict=True)
agent = project.agents.create_version(
    agent_name="claims-intake-agent",
    definition=PromptAgentDefinition(model="gpt-4o", instructions="...", tools=[tool]),
)
resp = openai_client.responses.create(
    input="Process this claim ...",
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
)
```

**2. LangGraph** — wire nodes and a conditional edge; the graph runs deterministically.
```python
g = StateGraph(GraphState)
g.add_node("classify", classify_node)
g.add_node("retrieve", retrieve_node)
g.add_edge(START, "classify")
g.add_conditional_edges("classify", route, {"escalate": "escalate", "retrieve": "retrieve"})
graph = g.compile()
result = graph.invoke({"message": "..."})
```

**3. Semantic Kernel** — register a plugin; invoke it (or let the model auto-call it).
```python
kernel = Kernel()
kernel.add_plugin(PolicyPlugin(), plugin_name="policy")            # @kernel_function inside
result = await kernel.invoke(plugin_name="policy", function_name="lookup_policy",
                             arguments=KernelArguments(policy_number="POL-12345"))
# or, with Azure: FunctionChoiceBehavior.Auto() lets the model call the plugin itself
```

---

## How to choose

- **Start on Microsoft Agent Framework / Foundry** if you're building on Azure and want managed agents,
  governance, identity, and the least operational burden — this is the course's architect's-default.
- **Reach for LangGraph** when the *control flow* is the hard part: explicit branches, retries, loops,
  cycles, durable checkpoints, and human-in-the-loop pauses you want to see and test as a graph.
- **Use Semantic Kernel** to embed AI "skills" (plugins) into an existing application, or when you want a
  thin, code-first kernel — especially across **.NET and Python**. See the SK + Azure data-service
  examples (PostgreSQL, AI Search, Cosmos DB) for plugins over real stores.

> **They overlap, and they're converging.** Microsoft has unified **AutoGen + Semantic Kernel** into the
> **Microsoft Agent Framework 1.0**. Skills you learn in SK (plugins, function calling) carry directly into
> the Agent Framework labs. LangGraph remains a strong, vendor-neutral choice for graph-shaped workflows and
> interoperates with Azure OpenAI via `langchain-openai`.

---

## See it run
Each framework has a runnable repo in this series — clone any and `uvicorn app.main:app --reload`:
- **Microsoft Agent Framework / Foundry:** the [12 weekly labs](https://github.com/satyajeetaiml-hue?tab=repositories&q=agentic-ai-azure) (start with [Week 2](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week02-foundry-claims))
- **LangGraph:** this repo ([agentic-ai-azure-langgraph](https://github.com/satyajeetaiml-hue/agentic-ai-azure-langgraph))
- **Semantic Kernel:** [agentic-ai-azure-semantic-kernel](https://github.com/satyajeetaiml-hue/agentic-ai-azure-semantic-kernel)
- **Semantic Kernel + Azure data services:** [PostgreSQL](https://github.com/satyajeetaiml-hue/agentic-ai-azure-sk-postgresql) (Orders Assistant) · [AI Search](https://github.com/satyajeetaiml-hue/agentic-ai-azure-sk-ai-search) (RAG) · [Cosmos DB](https://github.com/satyajeetaiml-hue/agentic-ai-azure-sk-cosmosdb) (durable memory)
- **Course hub:** [azure-agentic-ai-masterclass](https://github.com/satyajeetaiml-hue/azure-agentic-ai-masterclass)
