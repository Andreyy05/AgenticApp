from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

# ============================================================================
# User Input & Constraints
# ============================================================================

class TripInput(BaseModel):
    destination: str = Field(..., description="Target city/destination")
    origin: str = Field("PRG", description="Departure airport code or city")
    start_date: str = Field(..., description="YYYY-MM-DD")
    end_date: str = Field(..., description="YYYY-MM-DD")
    budget_usd: float = Field(..., description="Total trip budget in USD")
    pace: Literal["relaxed", "moderate", "fast-paced"] = Field("moderate", description="Desired travel pace")
    interests: List[str] = Field(default_factory=list, description="Traveler interests, e.g. history, food, art")
    dietary: List[str] = Field(default_factory=list, description="Dietary restrictions, e.g. vegetarian, vegan")


# ============================================================================
# Tool Input / Output Models
# ============================================================================

class WeatherDay(BaseModel):
    date: str
    temp_c: int
    condition: str
    is_rainy: bool
    recommended_clothing: str


class FlightOption(BaseModel):
    airline: str
    flight_number: str
    departure: str
    arrival: str
    price_usd: float
    stops: int


class LodgingOption(BaseModel):
    name: str
    type: str  # e.g. "Hotel", "Boutique Apartment", "Hostel"
    neighborhood: str
    nightly_rate_usd: float
    total_cost_usd: float
    rating: float


class AttractionOption(BaseModel):
    name: str
    category: str  # "Sightseeing", "Museum", "Food & Drink", "Walking Tour"
    cost_usd: float
    estimated_hours: float
    indoor: bool
    description: str


# ============================================================================
# Final Structured Output (Pydantic Schema)
# ============================================================================

class ActivitySlot(BaseModel):
    period: Literal["Morning", "Afternoon", "Evening"]
    title: str
    category: str
    cost_usd: float
    description: str
    weather_suitable: bool = True


class DayPlan(BaseModel):
    day_number: int
    date: str
    weather_summary: str
    morning: ActivitySlot
    afternoon: ActivitySlot
    evening: ActivitySlot
    estimated_food_cost_usd: float
    day_total_usd: float


class BudgetSummary(BaseModel):
    flights_cost_usd: float
    lodging_cost_usd: float
    activities_cost_usd: float
    meals_cost_usd: float
    total_spent_usd: float
    allocated_budget_usd: float
    remaining_usd: float
    within_budget: bool


class TripItinerary(BaseModel):
    destination: str
    travel_dates: str
    total_days: int
    flight: FlightOption
    lodging: LodgingOption
    day_by_day: List[DayPlan]
    budget_summary: BudgetSummary
    packing_and_travel_tips: List[str]
    agent_notes: str


# ============================================================================
# Agent Loop Trace & Audit Models
# ============================================================================

class StepRecord(BaseModel):
    step_number: int
    agent_state: str  # "THINKING", "CALLING_TOOL", "HANDLING_ERROR", "REPLANNING", "TERMINATING"
    thought: str
    tool_called: Optional[str] = None
    tool_arguments: Optional[Dict[str, Any]] = None
    tool_success: Optional[bool] = None
    tool_output: Optional[Any] = None
    error_message: Optional[str] = None
    replanning_note: Optional[str] = None


class RunTrace(BaseModel):
    run_id: str
    scenario_name: str
    input_parameters: TripInput
    total_steps: int
    encountered_errors: bool
    error_descriptions: List[str] = Field(default_factory=list)
    replanning_actions_taken: List[str] = Field(default_factory=list)
    steps: List[StepRecord]
    final_itinerary: Optional[TripItinerary] = None
    clean_termination: bool = True
