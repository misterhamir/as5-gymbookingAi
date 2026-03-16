# Architecture & Implementation Plan for OpenAI Booking Agent

Since you want to build this yourself, here is a complete architectural plan, folder structure, and step-by-step guide to help you build the Agent booking system.

## 1. Architectural Decision: One App vs Two Apps?

You asked whether you should create 2 different apps running concurrently. Both approaches are valid, but they serve different purposes:

### Approach A: The "Monolith" (1 App) - *Recommended for Beginners*
In this approach, you add the OpenAI code directly into your existing FastAPI application.
- **Pros:** Much easier to build. The Agent can directly access the database using your existing `sqlmodel` Database Sessions. You don't have to worry about network requests failing.
- **Cons:** Any time the Agent takes a few seconds to think, it's holding up the FastAPI thread. 
- **How it works:** You create a `POST /chat` endpoint in FastAPI. The user sends a message there, the endpoint talks to OpenAI, OpenAI returns tool calls (like "run the [create_schedule](file:///Users/userss/Documents/learning/indrazm/as5/as1_repo/app/router/schedule.py#21-33) function"), your endpoint runs the Python function directly against the database, and returns the final answer.

### Approach B: "Microservices" (2 Apps) - *More Realistic for Production*
In this approach, you leave your FastAPI App completely alone. You create a separate Python script or app (the "Agent App").
- **Pros:** Separation of concerns. Your FastAPI app just serves data. Your Agent app handles the heavy LLM logic.
- **Cons:** More complex. The Agent app must make HTTP requests (using the `requests` or `httpx` library) to `http://127.0.0.1:8000/schedule` to get data, rather than just querying the database directly.
- **How to run:** 
  1. Terminal 1: `make dev` (runs the FastAPI server)
  2. Terminal 2: `python my_agent.py` (runs the CLI chat interface)

---

## 2. Folder Structure Plan

If you decide to go with **Approach A (1 App)**, here is how your folder structure should look:

```text
as1_repo/
├── app/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── utils/
│   ├── router/
│   │   ├── bookings.py    <-- Existing
│   │   ├── schedule.py    <-- Existing
│   │   └── chat.py        <-- [NEW] Define your FastAPI POST /chat route here
│   ├── agent.py           <-- [NEW] Put your OpenAI client and Tool definitions here
│   └── main.py            <-- Import your new chat router here
├── pyproject.toml         <-- Add `openai` here
└── README.md
```

If you decide to go with **Approach B (2 Apps)**, you create a completely new folder alongside the gym API:

```text
as1_repo/                  <-- Only contains the FastAPI database code
agent_repo/                <-- [NEW FOLDER]
├── agent.py               <-- [NEW] The main script running your OpenAI logic
├── api_client.py          <-- [NEW] Helper functions that make HTTP GET/POST to http://127.0.0.1:8000
└── pyproject.toml         <-- Contains `openai` and `requests` dependencies
```

---

## 3. Step-by-Step Walkthrough to Build It Yourself

Here is how you can implement this step-by-step using **Approach A** (The Monolith).

### Step 1: Install Dependencies
Run `uv add openai` in your `as1_repo` folder to install the official OpenAI Python SDK.

### Step 2: Define Your Tools (in [agent.py](file:///Users/userss/Documents/learning/indrazm/as5/as1_repo/app/agent.py))
Create [app/agent.py](file:///Users/userss/Documents/learning/indrazm/as5/as1_repo/app/agent.py). In this file, you need to define the JSON schemas that tell OpenAI what your functions do. For example:
```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_schedules",
            "description": "Get all available gym class schedules.",
            "parameters": {"type": "object", "properties": {}},
        },
    }
]
```
Do this for checking schedules, making schedules, checking bookings, and making bookings.

### Step 3: Write the Tool Execution Logic
In the same file, write a function that takes the tool name chosen by OpenAI (e.g., `"get_schedules"`) and runs the actual database query:
```python
def execute_tool(tool_name, arguments_dict):
    if tool_name == "get_schedules":
        # Run DB query and return the schedules as a string
```

### Step 4: Write the Chat Loop
Create a function [chat_with_agent(user_message)](file:///Users/userss/Documents/learning/indrazm/as5/as1_repo/app/agent.py#125-170) that:
1. Calls `client.chat.completions.create(...)` with the user's message and the `TOOLS` list.
2. Checks if OpenAI returned a `tool_calls` request.
3. If yes, it runs the [execute_tool](file:///Users/userss/Documents/learning/indrazm/as5/as1_repo/app/agent.py#74-123) function, appends the result to the history, and calls OpenAI again to get the final answer.

### Step 5: Connect to FastAPI
Create [app/router/chat.py](file:///Users/userss/Documents/learning/indrazm/as5/as1_repo/app/router/chat.py) and define a `/chat` endpoint that receives a user message, passes it to the [chat_with_agent](file:///Users/userss/Documents/learning/indrazm/as5/as1_repo/app/agent.py#125-170) function from Step 4, and returns the result to the user.

---

> **Note**: I previously added the fully working code to your repository to demonstrate this! If you'd like me to revert those changes so you can start from a completely clean slate, please let me know.
