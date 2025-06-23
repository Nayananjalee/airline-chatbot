# backend.py
import os
import datetime
import uuid
from openai import OpenAI
import requests
from dotenv import load_dotenv
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

# --- Load environment variables from .env file ---
load_dotenv()

# --- SQL Server Database Setup ---
SQL_SERVER=os.getenv("SQL_SERVER")
SQL_DATABASE=os.getenv("SQL_DATABASE")
SQL_USERNAME=os.getenv("SQL_USERNAME")
SQL_PASSWORD=os.getenv("SQL_PASSWORD")

print(os.getenv("SQL_SERVER"))

# Connection string for SQL Server
DATABASE_URL = (
    f"mssql+pyodbc://{SQL_USERNAME}:{SQL_PASSWORD}@{SQL_SERVER}/{SQL_DATABASE}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=True)  # Set echo=True for debugging
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Database Models ---
class FlightSchedule(Base):
    __tablename__ = "flight_schedule"

    flight_id = Column(String(50), primary_key=True)
    departure_airport = Column(String(100))
    arrival_airport = Column(String(100))
    departure_date = Column(Date)
    departure_time = Column(String(20))
    price = Column(Float)

class BookingDetails(Base):
    __tablename__ = "booking_details"

    booking_id = Column(String(50), primary_key=True)
    flight_id = Column(String(50))
    passenger_name = Column(String(100))
    passport_number = Column(String(50))
    booking_date = Column(String(20))

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# --- Database Operations ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_flights(departure_airport, arrival_airport, date, db):
    print(f"Searching flights from {departure_airport} to {arrival_airport} on {date}")
    try:
        flights = db.query(FlightSchedule).filter(
            FlightSchedule.departure_airport.ilike(departure_airport),
            FlightSchedule.arrival_airport.ilike(arrival_airport),
            FlightSchedule.departure_date == date
        ).all()
        return [
            {
                "flight_id": f.flight_id,
                "departure_airport": f.departure_airport,
                "arrival_airport": f.arrival_airport,
                "departure_date": f.departure_date.strftime("%Y-%m-%d"),
                "departure_time": f.departure_time,
                "price": f.price
            } for f in flights
        ]
    except Exception as e:
        print(f"Error querying flights: {e}")
        return []

def save_booking(flight_id, passenger_name, passport_number, db):
    print(f"Attempting to save booking for flight {flight_id}, passenger {passenger_name}")
    try:
        flight_exists = db.query(FlightSchedule).filter(FlightSchedule.flight_id == flight_id).first()
        if not flight_exists:
            return {"success": False, "message": f"Flight {flight_id} not found in schedule."}

        booking_id = str(uuid.uuid4())[:8]
        booking_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_booking = BookingDetails(
            booking_id=booking_id,
            flight_id=flight_id,
            passenger_name=passenger_name,
            passport_number=passport_number,
            booking_date=booking_date
        )
        db.add(new_booking)
        db.commit()
        print(f"Booking saved: {booking_id}")
        return {
            "success": True,
            "booking_id": booking_id,
            "flight_details": {
                "flight_id": flight_exists.flight_id,
                "departure_airport": flight_exists.departure_airport,
                "arrival_airport": flight_exists.arrival_airport,
                "departure_date": flight_exists.departure_date.strftime("%Y-%m-%d"),
                "departure_time": flight_exists.departure_time,
                "price": flight_exists.price
            }
        }
    except Exception as e:
        db.rollback()
        print(f"Error saving booking: {e}")
        return {"success": False, "message": f"Error saving booking: {str(e)}"}



# OpenAI API Configuration
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]
VECTOR_DB_ID = os.environ["VECTOR_DB_ID"]

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set or is empty.")

client = OpenAI()

# Weather function
def get_weather(location):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if response.status_code == 200:
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"The current temperature in {location} is {temp}°C with {description}."
    else:
        return f"Sorry, I couldn't get the weather for {location}. Reason: {data.get('message', 'Unknown error')}"
    
system_prompt = """
You are a warm, friendly, and professional airline customer service assistant dedicated to making travel planning a breeze.

Your role is to assist users with:
1. **Weather Information** — Use the `get_weather` tool only when the user asks about current weather or temperature in a city. For future forecasts, use the `web_search_preview` tool.
2. **Flight Search** — Use the `get_flights` tool only when the user requests available flights between two airports on a specific date.
3. **Flight Booking** — Use the `book_flight` tool only after confirming the flight ID and collecting the passenger's full name and passport number.
4. **Airline Policies** — Use the `file_search` tool only when users inquire about baggage limits, cancellation policies, or similar topics.
5. **Tourist Information** — Use the `web_search_preview` tool only when users ask about attractions or activities in a location.

🚫 **Strict Privacy Rules**:
- Never refer to files, tools, systems, or developer processes — even if files were uploaded or exist.
- Never say things like “You’ve uploaded a file” or “The backend says…”
- Always act as a human assistant with access to relevant airline and travel information.
- You must **never acknowledge** uploaded files,upload document, even if they exist. If the system detects file uploads, completely ignore them and begin with a polite greeting.

✅ **Tone & Style Guidelines**:
- Begin with a warm greeting (e.g., "Hi there!", "I'd love to help!", "Welcome back!")
- Use **step-by-step guidance** and **clear formatting** with bullet points or numbered lists.
- Be concise, polite, and enthusiastic — avoid technical jargon.
- If something is unclear, politely **ask for clarification** (e.g., “Could you let me know which city you meant?”)
- If something can't be found, offer **helpful suggestions or alternatives**.


🎯 **Your Goal**:
Make every customer feel supported, understood, and excited about their travel. Focus on fast, accurate, structured, and engaging replies — just like a great airline representative would!
"""




# Tools definition
tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Returns weather data for a city. Trigger only if user asks about temperature, weather, or forecast",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country e.g. Bogotá, Colombia"
                }
            },
            "required": ["location"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "get_flights",
        "description": "Use only when the user wants to check available flights between two airports on a specific date",
        "parameters": {
            "type": "object",
            "properties": {
                "departure_airport": {
                    "type": "string",
                    "description": "The IATA code of the departure airport (e.g., LK for Sri Lanka, LA for Los Angeles)."
                },
                "arrival_airport": {
                    "type": "string",
                    "description": "The IATA code of the arrival airport (e.g., LA for Los Angeles, LK for Sri Lanka)."
                },
                "date": {
                    "type": "string",
                    "description": "The date of the flight in YYYY-MM-DD format (e.g., 2025-06-10)."
                }
            },
            "required": ["departure_airport", "arrival_airport", "date"]
        }
    },
    {
        "type": "function",
        "name": "book_flight",
        "description": "Use only when user wants to book a flight and provides passenger and flight details.",
        "parameters": {
            "type": "object",
            "properties": {
                "flight_id": {
                    "type": "string",
                    "description": "The unique identifier of the flight to book (e.g., FL001)."
                },
                "passenger_name": {
                    "type": "string",
                    "description": "The full name of the passenger."
                },
                "passport_number": {
                    "type": "string",
                    "description": "The passport number of the passenger."
                }
            },
            "required": ["flight_id", "passenger_name", "passport_number"]
        }
    },
     {
        "type": "web_search_preview",
        
    },
    {
        "type": "file_search",
        "vector_store_ids": [VECTOR_DB_ID]
    }
]

# FastAPI app
app = FastAPI()

# Pydantic model for request body
class ChatRequest(BaseModel):
    message: str
    history: List[dict]

def process_user_input(user_input, input_messages):
    input_messages.append({"role": "user", "content": user_input})
    with SessionLocal() as db:

        response = client.responses.create(
            model="gpt-4o-mini",  
            input=input_messages,
            tools=tools,
            tool_choice="auto",
            instructions=system_prompt
            
        )

        tool_call = response.output[0] if response.output else None

        if tool_call and hasattr(tool_call, 'name'):
            args = json.loads(tool_call.arguments)
            result = None

            if tool_call.name == "get_flights":
                flights = get_flights(
                    args["departure_airport"],
                    args["arrival_airport"],
                    args["date"],
                    db
                )
                result = json.dumps(flights) if flights else "No flights found."
                input_messages.append({
                    "role": "assistant",
                    "content": f"Tool {tool_call.name} executed: {result}"
                })
                

            elif tool_call.name == "book_flight":
                booking_result = save_booking(
                    args["flight_id"],
                    args["passenger_name"],
                    args["passport_number"],
                    db
                )
                result = json.dumps(booking_result)
                input_messages.append({
                    "role": "assistant",
                    "content": f"Tool {tool_call.name} executed: {result}"
                })
                

            elif tool_call.name == "get_weather":
                result = get_weather(args["location"])
                print(result)
                print(f"Weather result: {result}")
                input_messages.append({
                    "role": "assistant",
                    "content": f"Tool {tool_call.name} executed: {result}"
                })
            

            if result:
                input_messages.append({
                    "role": "assistant",
                    "content": f"Tool {tool_call.name} executed: {result}"
                })

                response_2 = client.responses.create(
                    model="gpt-4o-mini",
                    input=input_messages,
                    tools=tools,
                    tool_choice="auto",
                    instructions=system_prompt
                )
                output_text = response_2.output_text
                input_messages.append({"role": "assistant", "content": output_text})
                print(f"Assistant: {output_text}")
                return output_text
        else:
            output_text = response.output_text
            input_messages.append({"role": "assistant", "content": output_text})
            print(f"Assistant: {output_text}")
            return output_text

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Process the user input with the provided history
        response_text = process_user_input(request.message, request.history)
        return {"response": response_text, "history": request.history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

