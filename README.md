# Travel-Planner Agent — Autonomous Tool-Calling System

An autonomous, tool-calling agent implementation with an **explicit agent loop**, **structured Pydantic outputs**, **five domain tools**, **error handling & dynamic replanning**, and **complete execution traces** for multi-day travel planning.

---

## 🏛️ Architecture Sketch

The application separates user inputs, the explicit agent control loop, tool execution with validation, and strict Pydantic output serialization:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             USER INPUT (JSON / CLI)                         │
│  - Destination: "Paris" / "Tokyo"        - Pace: "relaxed" | "moderate"     │
│  - Dates: "2026-06-10" to "2026-06-13"   - Interests: ["art", "food", ...]  │
│  - Total Budget: $900.00 USD             - Dietary: ["vegetarian"]          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EXPLICIT AGENT LOOP (State Machine)                    │
│                                                                             │
│                   ┌─────────────────────────────┐                           │
│                   │         INITIALIZE          │                           │
│                   └──────────────┬──────────────┘                           │
│                                  │                                          │
│                                  ▼                                          │
│                   ┌─────────────────────────────┐                           │
│                   │      1. FETCH_WEATHER       │                           │
│                   └──────────────┬──────────────┘                           │
│                                  │ (Forecasts acquired)                     │
│                                  ▼                                          │
│                   ┌─────────────────────────────┐                           │
│         ┌────────►│      2. LOOKUP_FLIGHT       │                           │
│         │         └──────────────┬──────────────┘                           │
│         │                        │                                          │
│   (Budget Adjusted)      [Tool Error?]                                      │
│         │              YES ╱           ╲ NO                                 │
│         │                 ▼             ▼                                   │
│  ┌──────┴─────────┐ ┌───────────┐  ┌─────────────────────────┐              │
│  │   REPLANNING   │◄┤ TOOL_ERROR│  │    3. LOOKUP_LODGING    │              │
│  └────────────────┘ └───────────┘  └────────────┬────────────┘              │
│                                                 │                           │
│                                                 ▼                           │
│                                    ┌─────────────────────────┐              │
│                                    │  4. LOOKUP_ATTRACTIONS  │              │
│                                    └────────────┬────────────┘              │
│                                                 │                           │
│                                                 ▼                           │
│                                    ┌─────────────────────────┐              │
│                                    │  5. ASSEMBLE_ITINERARY  │              │
│                                    └────────────┬────────────┘              │
│                                                 │                           │
│                                                 ▼                           │
│                                    ┌─────────────────────────┐              │
│                                    │       TERMINATED        │              │
│                                    │   (Clean Exit + Trace)  │              │
│                                    └─────────────────────────┘              │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STRUCTURED OUTPUT & AUDIT TRAIL                          │
│  - DayPlan (Morning, Afternoon, Evening weather-compatible activities)      │
│  - BudgetSummary (Flights + Lodging + Activities + Food <= Total Budget)    │
│  - RunTrace (JSON & Markdown execution audit log in traces/)                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
[TripInput] ──► [Agent State]
                     │
                     ├──► tool_weather_lookup()      ──► [Daily Forecasts & Rain Flag]
                     ├──► tool_flight_lookup()       ──► [Selected Flight or NO_RESULTS]
                     │         ▲ (if error: replan)
                     ├──► tool_lodging_lookup()      ──► [Budget-Compliant Accommodation]
                     ├──► tool_attractions_lookup()  ──► [Filtered Points of Interest]
                     └──► tool_calendar_day_planner()──► [Structured TripItinerary (Pydantic)]
```

---

## 📋 Core System Capabilities

| Capability | Implementation Details | Status |
|---|---|---|
| **Explicit Agent Loop** | State-machine loop (`FETCH_WEATHER` → `LOOKUP_FLIGHT` → `LOOKUP_LODGING` → `LOOKUP_ATTRACTIONS` → `ASSEMBLE_ITINERARY` → `TERMINATED`) in `agent_loop.py` | ✅ Complete |
| **Structured Outputs** | Pydantic v2 schemas: `TripItinerary`, `DayPlan`, `ActivitySlot`, `BudgetSummary`, `FlightOption`, `LodgingOption` in `models.py` | ✅ Complete |
| **At Least Four Tools** | 5 tools implemented in `tools.py`: `weather_lookup`, `flight_lookup`, `lodging_lookup`, `attractions_lookup`, `calendar_day_planner` | ✅ Complete (5 tools) |
| **Tool Error Handling & Replanning** | Automatic detection of tool errors (e.g. `NO_FLIGHTS_UNDER_BUDGET`), budget rebalancing, fallback lodging selection, and clean termination | ✅ Complete |
| **Clean Termination** | Deterministic termination condition verifying full itinerary construction and budget validation | ✅ Complete |
| **Two Successful Run Traces** | Both JSON and Markdown traces saved in `traces/run_1_paris.*` and `traces/run_2_tokyo.*` | ✅ Complete |

---

## 📁 Repository Structure

```
AgenticApp/
├── models.py             # Pydantic v2 schemas (TripInput, DayPlan, BudgetSummary, TripItinerary, RunTrace)
├── tools.py              # 5 domain tools with input validation and edge-case error responses
├── agent_loop.py         # Explicit finite-state agent loop with error handling and budget replanning
├── run_agent.py          # CLI runner: executes evaluation traces + interactive custom planning mode
├── Spustit_Agenta.bat    # Windows one-click interactive launcher
├── requirements.txt      # Project dependencies (pydantic, rich)
├── tests/
│   └── test_agent.py     # Unittest test suite (6 passing test cases)
├── traces/
│   ├── run_1_paris.json  # Run 1 raw JSON trace (Paris 4-day baseline)
│   ├── run_1_paris.md    # Run 1 formatted Markdown execution trace
│   ├── run_2_tokyo.json  # Run 2 raw JSON trace (Tokyo error recovery & replanning)
│   └── run_2_tokyo.md    # Run 2 formatted Markdown execution trace
└── README.md             # Complete engineering documentation
```

---

## 🛠️ Tool Specifications (5 Tools Implemented)

All tools are modular, type-annotated, and validate input arguments before returning structured payloads or standardized error objects:

| Tool Name | Parameters | Returns | Error Handling Trigger |
|---|---|---|---|
| **`weather_lookup`** | `destination: str`<br>`start_date: str`<br>`end_date: str` | `{"success": bool, "forecasts": List[WeatherDay]}` | Catches `INVALID_DATE_RANGE` (e.g. end date before start date) or `UNSUPPORTED_DESTINATION`. |
| **`flight_lookup`** | `origin: str`<br>`destination: str`<br>`departure_date: str`<br>`return_date: str`<br>`max_price_usd: float` | `{"success": bool, "flights": List[FlightOption]}` | Returns `NO_FLIGHTS_UNDER_BUDGET` when all flights exceed `max_price_usd`, including lowest available price to assist replanning. |
| **`lodging_lookup`** | `destination: str`<br>`checkin_date: str`<br>`checkout_date: str`<br>`max_nightly_rate_usd: float` | `{"success": bool, "lodgings": List[LodgingOption]}` | Returns `NO_LODGING_UNDER_BUDGET` when rates exceed limit; validates minimum 1-night duration. |
| **`attractions_lookup`**| `destination: str`<br>`interests: List[str]`<br>`pace: str` | `{"success": bool, "attractions": List[AttractionOption]}` | Filters by category (art, history, anime, food); tags venues as indoor/outdoor for weather matching. |
| **`calendar_day_planner`**| `destination: str`<br>`flight: dict`<br>`lodging: dict`<br>`weather_forecasts: list`<br>`attractions: list`<br>`total_budget_usd: float` | `{"success": bool, "itinerary": TripItinerary}` | Synthesizes all gathered components into a validated Pydantic model; schedules indoor activities during rainy days. |

---

## 🔁 Agent Loop & Error Handling / Replanning Mechanics

The agent does **not** rely on uncontrolled recursive loops. Instead, it maintains an explicit while-loop (`while state != "TERMINATED" and step_count < max_steps:`) with state tracking:

### Error Recovery & Replanning Scenario (Demonstrated in Run 2):
1. **Initial Condition**: User requests a 5-day trip to Tokyo with an initial target flight budget of `$300.00 USD`.
2. **Tool Failure**: `flight_lookup` searches the inventory and finds the lowest commercial flight is Emirates at `$690.00 USD`. The tool returns:
   ```json
   {
     "success": false,
     "error_type": "NO_FLIGHTS_UNDER_BUDGET",
     "message": "No flights found from PRG to Tokyo under $300.00. The cheapest available option is with Emirates (EK318) at $690.00.",
     "lowest_available_price": 690.0
   }
   ```
3. **Agent State Transition (`HANDLING_ERROR` → `REPLANNING`)**:
   - The agent detects `success: false`.
   - Records the error in the audit trace: `trace.encountered_errors = True`.
   - Formulates a replanning strategy:
     - **Action 1**: Increases flight cap to `$740.00 USD` (accommodating the `$690.00` flight).
     - **Action 2**: Rebalances remaining budget by setting a strict lodging ceiling of `$60.00/night` (selecting capsule hotel at `$45.00/night` instead of luxury hotels).
4. **Tool Re-invocation**:
   - The agent re-invokes `flight_lookup` with the updated `$740.00` cap.
   - Emirates flight is successfully booked for `$690.00`.
   - Lodging is secured at `Nine Hours Capsule Akihabara` for `$180.00` total.
5. **Clean Termination**:
   - Total spent: `$1210.00 USD` out of `$1350.00 USD` budget limit (**$140.00 remaining buffer**).
   - Agent loop transitions to `TERMINATED` and outputs the validated Pydantic `TripItinerary`.

---

## ⚙️ Setup & Installation

### Prerequisites
- **Python 3.10+** (tested on Python 3.13)
- Windows PowerShell / Command Prompt or macOS / Linux bash.

### 1. Quick One-Click Setup (Windows)
Double-click:
```
Spustit_Agenta.bat
```
This presents an interactive menu to run the evaluation traces, start the interactive custom planner, or run unit tests.

### 2. Manual Command Line Setup

```powershell
# 1. Clone repository
git clone https://github.com/Andreyy05/AgenticApp.git
cd AgenticApp

# 2. Setup virtual environment & activate
python -m venv .venv
.\.venv\Scripts\activate
# (On Linux/macOS: source .venv/bin/activate)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the evaluation traces
python run_agent.py

# 5. Run the interactive planner
python run_agent.py --interactive

# 6. Run the unit test suite
python -m unittest tests/test_agent.py -v
```

---

## 📋 Example Inputs & Outputs

### Example 1: Paris Cultural 4-Day Trip (Baseline Smooth Run)

#### Input (`TripInput`)
```json
{
  "destination": "Paris",
  "origin": "PRG",
  "start_date": "2026-06-10",
  "end_date": "2026-06-13",
  "budget_usd": 900.0,
  "pace": "moderate",
  "interests": ["art", "museum", "history", "food"],
  "dietary": ["vegetarian"]
}
```

#### Execution Summary
- **Steps**: 5 loop iterations
- **Tool Errors**: None
- **Flight**: Air France AF1234 (`$210.00 USD`)
- **Lodging**: Montmartre Cozy Studio (`$255.00 USD` total for 3 nights)
- **Activities**: Louvre Museum, Musée d'Orsay, Sainte-Chapelle, Bakery Tasting (`$144.00 USD`)
- **Estimated Meals**: 4 days × $45.00 = `$180.00 USD`
- **Budget Result**: **$789.00 USD spent / $900.00 budget** (`$111.00 remaining balance`, `within_budget: true`)
- **Full Trace**: See [`traces/run_1_paris.md`](traces/run_1_paris.md) and [`traces/run_1_paris.json`](traces/run_1_paris.json).

---

### Example 2: Tokyo Budget Trip with Tool Error & Replanning

#### Input (`TripInput`)
```json
{
  "destination": "Tokyo",
  "origin": "PRG",
  "start_date": "2026-09-15",
  "end_date": "2026-09-19",
  "budget_usd": 1350.0,
  "pace": "moderate",
  "interests": ["pop culture", "tech", "food", "history"],
  "dietary": []
}
```

#### Execution Summary
- **Steps**: 6 loop iterations (includes error handling & replanning step)
- **Tool Error**: Step 2 encountered `NO_FLIGHTS_UNDER_BUDGET` when attempting initial $300 flight cap.
- **Replanning Decision**: Shifted budget allocation: increased flight cap to $740, selected capsule hotel ($45/night) to protect overall $1350 budget.
- **Flight**: Emirates EK318 (`$690.00 USD`)
- **Lodging**: Nine Hours Capsule Akihabara (`$180.00 USD` total for 4 nights)
- **Activities**: teamLab Borderless, Akihabara District, Tsukiji Food Tour, Skytree (`$165.00 USD`)
- **Estimated Meals**: 5 days × $35.00 = `$175.00 USD`
- **Budget Result**: **$1210.00 USD spent / $1350.00 budget** (`$140.00 remaining balance`, `within_budget: true`)
- **Full Trace**: See [`traces/run_2_tokyo.md`](traces/run_2_tokyo.md) and [`traces/run_2_tokyo.json`](traces/run_2_tokyo.json).

---

### Example 3: Interactive CLI Mode

Run `python run_agent.py --interactive` to plan any custom trip on the fly:

```
🧭 INTERAKTIVNÍ REŽIM: NAPLÁNUJTE SI VLASTNÍ CESTU
1. Cílové město (Paris / Tokyo) [výchozí: Paris]: Paris
2. Celkový rozpočet v USD [výchozí: 1000]: 800
3. Datum odjezdu (YYYY-MM-DD) [výchozí: 2026-06-10]: 2026-06-10
4. Datum návratu (YYYY-MM-DD) [výchozí: 2026-06-14]: 2026-06-13
5. Zájmy oddělené čárkou [výchozí: art, food]: art, food

>>> Spouštím agentní smyčku pro Paris...
[Step 1] weather_lookup -> Average temp 17°C
[Step 2] flight_lookup -> Air France AF1234 ($210.00)
[Step 3] lodging_lookup -> Montmartre Cozy Studio ($255.00)
[Step 4] attractions_lookup -> 3 matching attractions
[Step 5] calendar_day_planner -> Total spent: $761.00 / $800.00 ($39.00 buffer)
Terminated cleanly: True. Saved to traces/custom_interactive_run.md!
```

---

## 🧪 Unit Test Suite Verification

Run the test suite with:
```powershell
python -m unittest tests/test_agent.py -v
```

Output:
```text
test_agent_run_1_smooth (tests.test_agent.TestTravelPlannerAgent.test_agent_run_1_smooth) ... ok
test_agent_run_2_error_and_replanning (tests.test_agent.TestTravelPlannerAgent.test_agent_run_2_error_and_replanning) ... ok
test_flight_lookup_budget_error (tests.test_agent.TestTravelPlannerAgent.test_flight_lookup_budget_error) ... ok
test_lodging_lookup_success (tests.test_agent.TestTravelPlannerAgent.test_lodging_lookup_success) ... ok
test_weather_lookup_bad_dates (tests.test_agent.TestTravelPlannerAgent.test_weather_lookup_bad_dates) ... ok
test_weather_lookup_success (tests.test_agent.TestTravelPlannerAgent.test_weather_lookup_success) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.004s

OK
```
