import streamlit as st
import os
import requests
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
from agents.extensions.models.litellm_model import LitellmModel

load_dotenv()

@function_tool
def get_schedules():
    """function to retrieve all available gym classes."""
    try:
        response = requests.get("http://127.0.0.1:8000/schedule/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error connecting to server: {str(e)}"

@function_tool
def create_booking(user_id: int, schedule_id: int):
    """function to create a new booking for a user in a specific schedule slot."""
    try:
        response = requests.post(
            "http://127.0.0.1:8000/booking/",
            json={"booking_name": f"Booking_{user_id}_{schedule_id}", "user_id": user_id, "schedule_id": schedule_id}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error creating booking: {str(e)}"

agent = Agent(
    name="Gym Booking Agent",
    instructions="""You are a helpful gym receptionist.
    Help users view schedules and book classes.
    Always try to answer politely and call the necessary tools when appropriate.
    """,
    model=LitellmModel(
        model="openrouter/google/gemini-2.5-flash",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    ),
    tools=[get_schedules, create_booking],
)


st.title("Gym Booking AI")
st.write("Chat with our virtual receptionist to view classes and book your spot!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


if prompt := st.chat_input("Ask about classes or make a booking..."):
  
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
  
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
               
                import asyncio
                result = asyncio.run(Runner.run(starting_agent=agent, input=prompt))
                reply = result.final_output
            except Exception as e:
                reply = f"Sorry, I encountered an error: {str(e)}"
            
            st.markdown(reply)
            
  
    st.session_state.messages.append({"role": "assistant", "content": reply})
