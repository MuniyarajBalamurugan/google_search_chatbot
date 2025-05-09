from flask import Flask, request, jsonify, render_template
import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.tools import google_search
import os

os.environ["GOOGLE_API_KEY"] = "AIzaSyAWcLwMTK5xLqVTKEDUqGeYsNa_epIpHJk"  # Use secure method later

app = Flask(__name__)

# Initialize once
agent = Agent(
    name="search_agent",
    model="gemini-2.0-flash-exp",
    description="An agent that answers questions using Google Search.",
    instruction="Use the search tool to find answers to user queries.",
    tools=[google_search]
)
session_service = InMemorySessionService()
runner = Runner(agent=agent, app_name="search_app", session_service=session_service)
session_service.create_session(app_name="search_app", user_id="user1", session_id="session1")

async def call_agent_async(query: str):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."
    async for event in runner.run_async(user_id="user1", session_id="session1", new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No message.'}"
            break
    return final_response_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json['message']
    response = asyncio.run(call_agent_async(user_msg))
    return jsonify({'response': response})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Required for Render
    app.run(host="0.0.0.0", port=port)

