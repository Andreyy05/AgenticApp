from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from models import WeatherDay, FlightOption, LodgingOption, AttractionOption, DayPlan, ActivitySlot, BudgetSummary, TripItinerary

class ToolError(Exception):
    """Custom exception raised when a tool encounters bad input or fails."""
    pass


# ============================================================================
# Database of Mock Travel Data
# ============================================================================

DESTINATION_DATA = {
    "Paris": {
        "airport": "CDG",
        "avg_temp": 18,
        "flights": [
            FlightOption(airline="Air France", flight_number="AF1234", departure="09:15", arrival="11:00", price_usd=210.0, stops=0),
            FlightOption(airline="Smartwings", flight_number="QS1042", departure="14:30", arrival="16:15", price_usd=160.0, stops=0),
            FlightOption(airline="Lufthansa", flight_number="LH1890", departure="07:00", arrival="10:30", price_usd=280.0, stops=1),
        ],
        "lodgings": [
            LodgingOption(name="Hôtel Marais Bastille", type="Boutique Hotel", neighborhood="Le Marais", nightly_rate_usd=125.0, total_cost_usd=0.0, rating=4.7),
            LodgingOption(name="Montmartre Cozy Studio", type="Apartment", neighborhood="Montmartre", nightly_rate_usd=85.0, total_cost_usd=0.0, rating=4.5),
            LodgingOption(name="Generator Paris", type="Design Hostel (Private Room)", neighborhood="Canal Saint-Martin", nightly_rate_usd=60.0, total_cost_usd=0.0, rating=4.3),
            LodgingOption(name="Le Grand Quartier", type="4-Star Hotel", neighborhood="10th Arr.", nightly_rate_usd=195.0, total_cost_usd=0.0, rating=4.8),
        ],
        "attractions": [
            AttractionOption(name="Louvre Museum Masterpieces", category="Museum", cost_usd=22.0, estimated_hours=3.5, indoor=True, description="Explore the Mona Lisa, Venus de Milo and world-class French art collection."),
            AttractionOption(name="Eiffel Tower Summit & Champ de Mars", category="Sightseeing", cost_usd=30.0, estimated_hours=2.5, indoor=False, description="Ascend to the summit for panoramic skyline views and stroll the garden."),
            AttractionOption(name="Musée d'Orsay Impressionist Tour", category="Museum", cost_usd=18.0, estimated_hours=2.5, indoor=True, description="World's premier collection of Impressionist works in a converted railway station."),
            AttractionOption(name="Seine River Sunset Cruise", category="Sightseeing", cost_usd=17.0, estimated_hours=1.5, indoor=False, description="Romantic river cruise passing Notre-Dame, Conciergerie and illuminated bridges."),
            AttractionOption(name="Montmartre & Sacré-Cœur Walking Tour", category="Walking Tour", cost_usd=0.0, estimated_hours=2.0, indoor=False, description="Stroll cobblestone bohemian streets, artists' square and hilltop basilica."),
            AttractionOption(name="French Bakery & Patisserie Tasting", category="Food & Drink", cost_usd=25.0, estimated_hours=2.0, indoor=True, description="Sample warm croissants, artisanal baguettes, and delicate macarons."),
            AttractionOption(name="Sainte-Chapelle Stained Glass", category="History", cost_usd=14.0, estimated_hours=1.0, indoor=True, description="Radiant 13th-century Gothic chapel famous for jewel-like stained glass windows."),
            AttractionOption(name="Luxembourg Gardens Picnic & Stroll", category="Relaxation", cost_usd=0.0, estimated_hours=1.5, indoor=False, description="Sit by the Medici fountain amidst French formal gardens and tree-lined avenues."),
        ],
        "daily_meal_estimate": 45.0,
    },
    "Tokyo": {
        "airport": "HND",
        "avg_temp": 22,
        "flights": [
            FlightOption(airline="All Nippon Airways (ANA)", flight_number="NH210", departure="11:30", arrival="08:45 (+1)", price_usd=780.0, stops=1),
            FlightOption(airline="Emirates", flight_number="EK318", departure="15:45", arrival="17:20 (+1)", price_usd=690.0, stops=1),
            FlightOption(airline="Qatar Airways", flight_number="QR806", departure="22:15", arrival="23:30 (+1)", price_usd=720.0, stops=1),
        ],
        "lodgings": [
            LodgingOption(name="Shinjuku Granbell Hotel", type="Modern Hotel", neighborhood="Shinjuku", nightly_rate_usd=110.0, total_cost_usd=0.0, rating=4.6),
            LodgingOption(name="Asakusa Kokono Club Hotel", type="Boutique Ryokan", neighborhood="Asakusa", nightly_rate_usd=85.0, total_cost_usd=0.0, rating=4.7),
            LodgingOption(name="Nine Hours Capsule Akihabara", type="Capsule Hotel", neighborhood="Akihabara", nightly_rate_usd=45.0, total_cost_usd=0.0, rating=4.2),
            LodgingOption(name="Cerulean Tower Tokyu", type="Luxury Hotel", neighborhood="Shibuya", nightly_rate_usd=260.0, total_cost_usd=0.0, rating=4.9),
        ],
        "attractions": [
            AttractionOption(name="Senso-ji Temple & Nakamise Street", category="History", cost_usd=0.0, estimated_hours=2.0, indoor=False, description="Tokyo's oldest Buddhist temple and traditional market street."),
            AttractionOption(name="teamLab Borderless Digital Art Museum", category="Art & Tech", cost_usd=35.0, estimated_hours=3.0, indoor=True, description="Mesmerizing interactive digital art installations with no boundaries."),
            AttractionOption(name="Shibuya Crossing & Hachiko Memorial", category="Sightseeing", cost_usd=0.0, estimated_hours=1.5, indoor=False, description="The world's busiest pedestrian scramble crossing and iconic meeting spot."),
            AttractionOption(name="Akihabara Electronics & Anime District", category="Pop Culture", cost_usd=0.0, estimated_hours=3.0, indoor=True, description="Explore multi-floor retro gaming arcades, manga shops, and tech emporiums."),
            AttractionOption(name="Meiji Shrine & Yoyogi Park", category="Nature", cost_usd=0.0, estimated_hours=2.0, indoor=False, description="Tranquil forested Shinto shrine in the center of Tokyo."),
            AttractionOption(name="Tsukiji Outer Market Food Tour", category="Food & Drink", cost_usd=30.0, estimated_hours=2.0, indoor=False, description="Fresh tamagoyaki, matcha sweets, and authentic street food snacks."),
            AttractionOption(name="Tokyo Skytree Observation Deck", category="Sightseeing", cost_usd=24.0, estimated_hours=2.0, indoor=True, description="Breathtaking vistas across the Kanto plain with views of Mount Fuji on clear days."),
            AttractionOption(name="Ghibli Museum Mitaka", category="Culture", cost_usd=10.0, estimated_hours=2.5, indoor=True, description="Whimsical animation wonderland designed by legendary director Hayao Miyazaki."),
        ],
        "daily_meal_estimate": 35.0,
    },
}


# ============================================================================
# TOOL 1: Weather Lookup
# ============================================================================

def tool_weather_lookup(destination: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Looks up daily weather forecast for destination between start_date and end_date (YYYY-MM-DD).
    Handles date validation and unsupported destination errors.
    """
    # 1. Input validation
    if destination not in DESTINATION_DATA:
        return {
            "success": False,
            "error_type": "UNSUPPORTED_DESTINATION",
            "message": f"Weather service has no historical forecast for '{destination}'. Supported cities: {list(DESTINATION_DATA.keys())}."
        }

    try:
        d_start = datetime.strptime(start_date, "%Y-%m-%d")
        d_end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return {
            "success": False,
            "error_type": "BAD_DATE_FORMAT",
            "message": f"Dates must be in format YYYY-MM-DD. Received start='{start_date}', end='{end_date}'."
        }

    if d_end < d_start:
        return {
            "success": False,
            "error_type": "INVALID_DATE_RANGE",
            "message": f"End date ({end_date}) cannot be before start date ({start_date})."
        }

    num_days = (d_end - d_start).days + 1
    if num_days > 14:
        return {
            "success": False,
            "error_type": "RANGE_TOO_LARGE",
            "message": f"Weather service only supports forecasts up to 14 days. Requested {num_days} days."
        }

    # Generate realistic forecast (e.g. Day 2 has rain to test indoor replanning logic)
    forecasts: List[WeatherDay] = []
    base_temp = DESTINATION_DATA[destination]["avg_temp"]

    conditions_cycle = [
        ("Sunny", False, "Light breathable layers, sunglasses"),
        ("Light Rain / Showers", True, "Waterproof jacket or umbrella, warm layer"),
        ("Partly Cloudy", False, "Casual comfortable clothing, light sweater for evening"),
        ("Clear Sky", False, "Comfortable walking shoes, sun hat"),
        ("Overcast", False, "Windbreaker and comfortable layers"),
    ]

    for i in range(num_days):
        day_date = (d_start + timedelta(days=i)).strftime("%Y-%m-%d")
        cond, rainy, clothing = conditions_cycle[i % len(conditions_cycle)]
        temp = base_temp + (i % 3) - 1
        forecasts.append(WeatherDay(
            date=day_date,
            temp_c=temp,
            condition=cond,
            is_rainy=rainy,
            recommended_clothing=clothing
        ))

    return {
        "success": True,
        "destination": destination,
        "total_days": num_days,
        "forecasts": [f.model_dump() for f in forecasts]
    }


# ============================================================================
# TOOL 2: Flight Price Lookup
# ============================================================================

def tool_flight_lookup(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    max_price_usd: Optional[float] = None
) -> Dict[str, Any]:
    """
    Searches for flights from origin to destination.
    Returns available flight options, or returns NO_RESULTS if max_price_usd is too low.
    """
    if destination not in DESTINATION_DATA:
        return {
            "success": False,
            "error_type": "UNKNOWN_AIRPORT",
            "message": f"No commercial flight routes cataloged for destination '{destination}'."
        }

    available_flights = DESTINATION_DATA[destination]["flights"]
    cheapest_flight = min(available_flights, key=lambda f: f.price_usd)

    # Error handling trigger: Budget constraint check
    if max_price_usd is not None and max_price_usd < cheapest_flight.price_usd:
        return {
            "success": False,
            "error_type": "NO_FLIGHTS_UNDER_BUDGET",
            "message": (
                f"No flights found from {origin} to {destination} under ${max_price_usd:.2f}. "
                f"The cheapest available option is with {cheapest_flight.airline} ({cheapest_flight.flight_number}) "
                f"at ${cheapest_flight.price_usd:.2f}."
            ),
            "lowest_available_price": cheapest_flight.price_usd,
            "cheapest_flight": cheapest_flight.model_dump()
        }

    # Filter flights under budget if specified
    matching = [f for f in available_flights if max_price_usd is None or f.price_usd <= max_price_usd]

    return {
        "success": True,
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "flights": [f.model_dump() for f in matching]
    }


# ============================================================================
# TOOL 3: Hotel / Lodging Lookup
# ============================================================================

def tool_lodging_lookup(
    destination: str,
    checkin_date: str,
    checkout_date: str,
    max_nightly_rate_usd: Optional[float] = None,
    preferred_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Searches lodging in the destination city.
    Calculates total cost for the exact duration of the stay.
    """
    if destination not in DESTINATION_DATA:
        return {
            "success": False,
            "error_type": "UNSUPPORTED_DESTINATION",
            "message": f"Lodging registry does not include '{destination}'."
        }

    try:
        d1 = datetime.strptime(checkin_date, "%Y-%m-%d")
        d2 = datetime.strptime(checkout_date, "%Y-%m-%d")
        nights = (d2 - d1).days
        if nights < 1:
            return {
                "success": False,
                "error_type": "INVALID_STAY_DURATION",
                "message": f"Checkout date ({checkout_date}) must be at least 1 night after checkin ({checkin_date})."
            }
    except ValueError:
        return {
            "success": False,
            "error_type": "BAD_DATE_FORMAT",
            "message": "Checkin and checkout dates must be formatted as YYYY-MM-DD."
        }

    raw_lodgings = DESTINATION_DATA[destination]["lodgings"]
    results: List[LodgingOption] = []

    for item in raw_lodgings:
        total = round(item.nightly_rate_usd * nights, 2)
        lodging_with_total = LodgingOption(
            name=item.name,
            type=item.type,
            neighborhood=item.neighborhood,
            nightly_rate_usd=item.nightly_rate_usd,
            total_cost_usd=total,
            rating=item.rating
        )
        if max_nightly_rate_usd is None or lodging_with_total.nightly_rate_usd <= max_nightly_rate_usd:
            if preferred_type is None or preferred_type.lower() in lodging_with_total.type.lower():
                results.append(lodging_with_total)

    if not results:
        min_nightly = min(l.nightly_rate_usd for l in raw_lodgings)
        return {
            "success": False,
            "error_type": "NO_LODGING_UNDER_BUDGET",
            "message": (
                f"No accommodations found in {destination} under ${max_nightly_rate_usd:.2f}/night. "
                f"Lowest rate available is ${min_nightly:.2f}/night."
            ),
            "min_nightly_rate": min_nightly
        }

    return {
        "success": True,
        "destination": destination,
        "total_nights": nights,
        "lodgings": [r.model_dump() for r in results]
    }


# ============================================================================
# TOOL 4: Attractions & Activities Lookup
# ============================================================================

def tool_attractions_lookup(
    destination: str,
    interests: Optional[List[str]] = None,
    pace: str = "moderate"
) -> Dict[str, Any]:
    """
    Retrieves attractions and sights for destination filtered by traveler interests.
    """
    if destination not in DESTINATION_DATA:
        return {
            "success": False,
            "error_type": "UNSUPPORTED_DESTINATION",
            "message": f"Attraction catalog has no entries for '{destination}'."
        }

    all_attractions = DESTINATION_DATA[destination]["attractions"]
    
    # Filter or rank by interests
    if interests:
        normalized_interests = [i.lower() for i in interests]
        matched = []
        for a in all_attractions:
            # Check if category or description contains any interest
            if any(ni in a.category.lower() or ni in a.description.lower() or ni in a.name.lower() for ni in normalized_interests):
                matched.append(a)
        # If no specific interest matched, fallback to all attractions
        final_list = matched if matched else all_attractions
    else:
        final_list = all_attractions

    return {
        "success": True,
        "destination": destination,
        "matched_count": len(final_list),
        "attractions": [a.model_dump() for a in final_list]
    }


# ============================================================================
# TOOL 5: Calendar Day-Planner Helper (Itinerary Assembler)
# ============================================================================

def tool_calendar_day_planner(
    destination: str,
    flight: Dict[str, Any],
    lodging: Dict[str, Any],
    weather_forecasts: List[Dict[str, Any]],
    attractions: List[Dict[str, Any]],
    total_budget_usd: float,
    dietary: Optional[List[str]] = None,
    agent_notes: str = ""
) -> Dict[str, Any]:
    """
    Synthesizes flight, lodging, weather forecasts, and attractions into a cohesive,
    budget-compliant Day-by-Day itinerary adhering strictly to the Pydantic schema.
    """
    total_days = len(weather_forecasts)
    daily_meal_rate = DESTINATION_DATA.get(destination, {}).get("daily_meal_estimate", 40.0)

    # Dietary adjustment notes
    dietary_str = f" ({', '.join(dietary)})" if dietary else ""

    day_plans: List[DayPlan] = []
    total_activities_cost = 0.0
    attr_idx = 0
    num_attractions = len(attractions)

    for i, w in enumerate(weather_forecasts):
        day_num = i + 1
        is_rainy = w.get("is_rainy", False)
        cond = w.get("condition", "Sunny")
        temp = w.get("temp_c", 20)

        # Pick attractions, prioritizing indoor ones on rainy days
        morning_attr = None
        afternoon_attr = None

        # Search for indoor if rainy
        for offset in range(num_attractions):
            candidate = attractions[(attr_idx + offset) % num_attractions]
            if is_rainy:
                if candidate.get("indoor", True):
                    morning_attr = candidate
                    attr_idx = (attr_idx + offset + 1) % num_attractions
                    break
            else:
                morning_attr = candidate
                attr_idx = (attr_idx + offset + 1) % num_attractions
                break
        
        if not morning_attr:
            morning_attr = attractions[0]

        # Pick afternoon
        afternoon_attr = attractions[attr_idx % num_attractions]
        attr_idx = (attr_idx + 1) % num_attractions

        m_cost = morning_attr.get("cost_usd", 0.0)
        a_cost = afternoon_attr.get("cost_usd", 0.0)
        e_cost = 0.0  # Evening stroll / relaxed dinner

        total_activities_cost += m_cost + a_cost + e_cost
        day_food_cost = daily_meal_rate

        morning_slot = ActivitySlot(
            period="Morning",
            title=morning_attr.get("name", "Morning Exploration"),
            category=morning_attr.get("category", "Sightseeing"),
            cost_usd=m_cost,
            description=f"{morning_attr.get('description', '')} ({'Indoor suitable for rain' if is_rainy else 'Ideal morning conditions'}).",
            weather_suitable=True
        )

        afternoon_slot = ActivitySlot(
            period="Afternoon",
            title=afternoon_attr.get("name", "Afternoon Discovery"),
            category=afternoon_attr.get("category", "Culture"),
            cost_usd=a_cost,
            description=afternoon_attr.get("description", "Afternoon cultural exploration"),
            weather_suitable=True
        )

        evening_slot = ActivitySlot(
            period="Evening",
            title=f"Local Dining & Evening Stroll{dietary_str}",
            category="Dining & Leisure",
            cost_usd=0.0,
            description=f"Enjoy dinner in neighborhood near {lodging.get('neighborhood', 'center')}. Sample local specialties.",
            weather_suitable=True
        )

        day_total = m_cost + a_cost + e_cost + day_food_cost

        day_plans.append(DayPlan(
            day_number=day_num,
            date=w.get("date", f"Day {day_num}"),
            weather_summary=f"{cond}, {temp}°C - {w.get('recommended_clothing', 'Comfortable layers')}",
            morning=morning_slot,
            afternoon=afternoon_slot,
            evening=evening_slot,
            estimated_food_cost_usd=day_food_cost,
            day_total_usd=round(day_total, 2)
        ))

    flight_cost = flight.get("price_usd", 0.0)
    lodging_cost = lodging.get("total_cost_usd", 0.0)
    total_meals_cost = daily_meal_rate * total_days
    total_spent = flight_cost + lodging_cost + total_activities_cost + total_meals_cost
    remaining = total_budget_usd - total_spent
    within_budget = total_spent <= total_budget_usd

    budget_summary = BudgetSummary(
        flights_cost_usd=round(flight_cost, 2),
        lodging_cost_usd=round(lodging_cost, 2),
        activities_cost_usd=round(total_activities_cost, 2),
        meals_cost_usd=round(total_meals_cost, 2),
        total_spent_usd=round(total_spent, 2),
        allocated_budget_usd=round(total_budget_usd, 2),
        remaining_usd=round(remaining, 2),
        within_budget=within_budget
    )

    itinerary = TripItinerary(
        destination=destination,
        travel_dates=f"{weather_forecasts[0].get('date')} to {weather_forecasts[-1].get('date')}",
        total_days=total_days,
        flight=FlightOption(**flight),
        lodging=LodgingOption(**lodging),
        day_by_day=day_plans,
        budget_summary=budget_summary,
        packing_and_travel_tips=[
            f"Expected weather varies between {min(w.get('temp_c', 20) for w in weather_forecasts)}°C and {max(w.get('temp_c', 20) for w in weather_forecasts)}°C.",
            "Comfortable broken-in walking shoes are essential.",
            "Pre-book museum time slots online to skip queue lines.",
            f"Dietary focus: {', '.join(dietary) if dietary else 'Standard local cuisine'}."
        ],
        agent_notes=agent_notes or "Itinerary assembled successfully within budgetary and schedule constraints."
    )

    return {
        "success": True,
        "itinerary": itinerary.model_dump()
    }
