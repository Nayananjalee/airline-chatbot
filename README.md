# ✈️ Airline Customer Service Chat Agent

This is an AI-powered airline customer service chat agent designed to assist users with common airline queries using external APIs, simulated internal databases, and document processing.

## 🧠 Project Objective

To build a smart, conversational agent that can:
- Provide destination weather updates
- Check flight status and availability
- Handle flight bookings via a simulated database
- Answer FAQs from static airline documents
- Fetch real-time info from the web
- Offer a clean and simple user interface for interaction

## 🚀 Features

1. **🌤️ External API Integration**
   - Uses OpenWeatherMap API to fetch weather updates for any city or airport.
   - Example: _“What’s the weather like in New York tomorrow?”_

2. **🛫 Simulated Internal Database**
   - Queries flight schedules and handles mock bookings.
   - Example: _“Book a flight from LK to LA on June 10.”_

3. **📄 Document-Based FAQ Answering**
   - Parses a static document (PDF/Text) containing airline FAQs.
   - Example: _“What’s the baggage limit for international flights?”_

4. **🌐 Web Searching**
   - Uses web search tools to answer destination-related queries.
   - Example: _“What are the top 10 attractions in LA?”_

5. **🖥️ UI**
   - Frontend built with Next.js for clean user experience.
   - Allows real-time interaction with the chat agent.

## 🛠️ Tech Stack

- **Frontend**: Next.js (or alternative React framework)
- **Backend**: Python
- **APIs**:
  - OpenAI Responses API (`gpt-4o-mini`)
  - OpenWeatherMap API
- **Database**: SQL  SSMS 
- **Others**: File parsing, web search integration

## 🗂️ Folder Structure

```bash
├── frontend/                # Next.js app
├── backend/                 # Python API backend
├── database/                # SQL schema & mock data
├── docs/                    # FAQ PDF/document
├── .env                     # API keys (excluded in git)
└── README.md
