# Complete Tutorial (Microservice Architecture): FastAPI Booking System + Separate OpenAI Agent App

This tutorial will guide you through building a Gym Booking API using FastAPI and SQLModel. Then, we will build a **completely separate OpenAI Agent Application** that acts as a "client" and uses HTTP requests to communicate with your database backend.

---

## 1. High-Level Folder Structure

In this approach, you will have two entirely separate Python projects running side-by-side.

```text
as5/
├── gym_backend/           <-- [App 1] The FastAPI & Database Server
│   ├── alembic/
│   ├── alembic.ini
│   ├── database.db
│   ├── pyproject.toml
│   └── app/
│       ├── models/
│       ├── schemas/
│       ├── router/
│       └── main.py
│
└── agent_client/          <-- [App 2] The OpenAI Agent App
    ├── .env               <-- OpenAI API Key goes here
    ├── pyproject.toml     
    ├── api_client.py      <-- Helper to make HTTP requests to gym_backend
    └── main.agent.py      <-- The CLI chat loop
```

---

## Part 1: Building the Gym Backend (`gym_backend`)

First, we set up the database and FastAPI server. This acts solely as an API that holds data.

### Step 1: Project Setup
Create the folder and install dependencies:
```bash
mkdir gym_backend
cd gym_backend
uv init
uv add fastapi uvicorn sqlmodel alembic pydantic
```

### Step 2: Database Connection (`gym_backend/app/models/engine.py`)
```python
from sqlmodel import create_engine, Session

engine = create_engine("sqlite:///database.db", echo=True)

def get_db():
    with Session(engine) as session:
        yield session
```

### Step 3: Define Data Models (`gym_backend/app/models/database.py`)
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

class Schedule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    class_name: str
    instructor: str
    start_time: datetime
    end_time: datetime

class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    booking_name: str
    user_id: int = Field(foreign_key="user.id")
    schedule_id: int = Field(foreign_key="schedule.id")
```

*(You will then run `alembic init alembic`, update [alembic.ini](file:///Users/userss/Documents/learning/indrazm/as5/as1_repo/alembic.ini) and `env.py`, and run `alembic revision --autogenerate && alembic upgrade head` just like in the Monolith tutorial to create the `database.db`)*

### Step 4: API Validation Schemas (`gym_backend/app/schemas/bookings.py`)
```python
from pydantic import BaseModel
from datetime import datetime

class ScheduleRequest(BaseModel):
    class_name: str
    instructor: str
    start_time: datetime
    end_time: datetime

class BookingRequest(BaseModel):
    booking_name: str
    user_id: int
    schedule_id: int
```

### Step 5: Create API Routes (`gym_backend/app/router/schedule.py` & [bookings.py](file:///Users/userss/Documents/learning/indrazm/as5/as1_repo/app/router/bookings.py))
```python
# app/router/schedule.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.models.engine import get_db
from app.models.database import Schedule
from app.schemas.bookings import ScheduleRequest

schedule_router = APIRouter(prefix="/schedule", tags=["Schedule"])

@schedule_router.get("/")
def get_schedules(db: Session = Depends(get_db)):
    return db.exec(select(Schedule)).all()

@schedule_router.post("/")
def create_schedule(schedule_in: ScheduleRequest, db: Session = Depends(get_db)):
    new_schedule = Schedule(**schedule_in.model_dump())
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule
```
*(Similarly, create [bookings.py](file:///Users/userss/Documents/learning/indrazm/as5/as1_repo/app/router/bookings.py) for standard GET/POST endpoints).*

### Step 6: The Main Application (`gym_backend/app/main.py`)
```python
from fastapi import FastAPI
from app.router.schedule import schedule_router
from app.router.bookings import booking_router

app = FastAPI(title="Gym Booking API")
app.include_router(schedule_router)
app.include_router(booking_router)
```

**To run the backend:** open a terminal in `gym_backend` and run:
`uv run uvicorn app.main:app --reload` (Runs on http://127.0.0.1:8000)

---

## Part 2: Building the OpenAI Agent Client (`agent_client`)

Now, open a **brand new terminal window** (keep your backend running in the first one).

### Step 7: Agent Project Setup
Go back to the root `as5` folder and create the client folder:
```bash
cd ..
mkdir agent_client
cd agent_client
uv init
uv add openai httpx python-dotenv
```

### Step 8: Create an API HTTP Helper (`agent_client/api_client.py`)
Because the Agent is a separate app, it cannot read the SQLite database directly. It must make network calls to your FastAPI server! We will use the `httpx` library for this.

```python
# agent_client/api_client.py
import httpx

FASTAPI_URL = "http://127.0.0.1:8000"

def fetch_schedules():
    res = httpx.get(f"{FASTAPI_URL}/schedule/")
    return res.json()

def post_schedule(class_name, instructor, start_time, end_time):
    res = httpx.post(f"{FASTAPI_URL}/schedule/", json={
        "class_name": class_name,
        "instructor": instructor,
        "start_time": start_time,
        "end_time": end_time
    })
    return res.json()
    
# Add helpers for fetch_bookings and post_booking...
```

### Step 9: The Agent Application (`agent_client/main_agent.py`)
This is the script the user will run to chat. It uses your `api_client` helpers to execute its tools out over the network to the backend server.

```python
# agent_client/main_agent.py
import os
import json
from openai import OpenAI
import api_client

# Assumes you run `export OPENAI_API_KEY="..."` before running this script
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 1. Define Tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_schedules",
            "description": "Get all available gym class schedules.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_schedule",
            "description": "Create a new gym class schedule.",
            "parameters": {
                "type": "object",
                "properties": {
                    "class_name": {"type": "string", "description": "e.g., Yoga"},
                    "instructor": {"type": "string"},
                    "start_time": {"type": "string", "description": "ISO format time"},
                    "end_time": {"type": "string", "description": "ISO format time"}
                },
                "required": ["class_name", "instructor", "start_time", "end_time"]
            },
        },
    }
]

# 2. Network-based Execution Logic
def execute_tool_call(tool_call):
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    
    try:
        if name == "get_schedules":
            schedules = api_client.fetch_schedules()
            return json.dumps(schedules)
            
        elif name == "create_schedule":
            new_schedule = api_client.post_schedule(
                args["class_name"], args["instructor"], 
                args["start_time"], args["end_time"]
            )
            return json.dumps(new_schedule)
            
        else:
            return json.dumps({"error": "Unknown tool"})
    except Exception as e: # Catch network failures (e.g. FastAPI server is down)
        return json.dumps({"error": f"API request failed: {str(e)}"})

# 3. CLI Agent Loop
def run_cli_agent():
    print("Welcome to the Gym Booking Agent! Type 'exit' to quit.\n")
    messages = []
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        messages.append({"role": "user", "content": user_input})
        
        # Ask OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = response.choices[0].message
        
        # Tool Calling Block
        if msg.tool_calls:
            messages.append(msg.model_dump(exclude_unset=True))
            
            for tool_call in msg.tool_calls:
                print(f"[Agent is calculating: running {tool_call.function.name} over the network...]")
                result = execute_tool_call(tool_call)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": result
                })
                
            final_res = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
            final_msg = final_res.choices[0].message
            messages.append(final_msg.model_dump(exclude_unset=True))
            print(f"Agent: {final_msg.content}\n")
            
        else:
            messages.append(msg.model_dump(exclude_unset=True))
            print(f"Agent: {msg.content}\n")

if __name__ == "__main__":
    run_cli_agent()
```

---

## Part 3: Running the Microservices Together

Because these are two different applications, you need two terminals.

**Terminal 1 (The Data Server):**
```bash
cd gym_backend
uv run uvicorn app.main:app --reload
```
*(Leave this running.)*

**Terminal 2 (The Agent Client):**
```bash
cd agent_client
export OPENAI_API_KEY="sk-your-openai-key-here"
python main_agent.py
```

You can now chat with your CLI app in Terminal 2. When you assign it a task (like checking the schedule), you'll actually be able to see the HTTP `GET` and `POST` requests hit your FastAPI server logs over in Terminal 1!
