import unittest
from models import TripInput, TripItinerary
from tools import (
    tool_weather_lookup,
    tool_flight_lookup,
    tool_lodging_lookup,
    tool_attractions_lookup,
    tool_calendar_day_planner,
)
from agent_loop import TravelPlannerAgent


class TestTravelPlannerAgent(unittest.TestCase):

    def test_weather_lookup_success(self):
        res = tool_weather_lookup("Paris", "2026-06-10", "2026-06-13")
        self.assertTrue(res["success"])
        self.assertEqual(len(res["forecasts"]), 4)

    def test_weather_lookup_bad_dates(self):
        res = tool_weather_lookup("Paris", "2026-06-15", "2026-06-10")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_type"], "INVALID_DATE_RANGE")

    def test_flight_lookup_budget_error(self):
        # Flight prices to Tokyo start at $690; $200 should fail and return lowest available
        res = tool_flight_lookup("PRG", "Tokyo", "2026-09-15", "2026-09-19", max_price_usd=200.0)
        self.assertFalse(res["success"])
        self.assertEqual(res["error_type"], "NO_FLIGHTS_UNDER_BUDGET")
        self.assertIn("lowest_available_price", res)

    def test_lodging_lookup_success(self):
        res = tool_lodging_lookup("Paris", "2026-06-10", "2026-06-13")
        self.assertTrue(res["success"])
        self.assertGreater(len(res["lodgings"]), 0)

    def test_agent_run_1_smooth(self):
        agent = TravelPlannerAgent()
        trip_in = TripInput(
            destination="Paris",
            origin="PRG",
            start_date="2026-06-10",
            end_date="2026-06-13",
            budget_usd=900.0,
            pace="moderate",
            interests=["art", "museum"],
            dietary=["vegetarian"]
        )
        trace = agent.run(trip_in, scenario_name="Test Paris")
        self.assertTrue(trace.clean_termination)
        self.assertFalse(trace.encountered_errors)
        self.assertIsNotNone(trace.final_itinerary)
        self.assertTrue(trace.final_itinerary.budget_summary.within_budget)

    def test_agent_run_2_error_and_replanning(self):
        agent = TravelPlannerAgent()
        trip_in = TripInput(
            destination="Tokyo",
            origin="PRG",
            start_date="2026-09-15",
            end_date="2026-09-19",
            budget_usd=1350.0,
            pace="moderate",
            interests=["anime", "food"]
        )
        trace = agent.run(trip_in, scenario_name="Test Tokyo Budget Error")
        self.assertTrue(trace.clean_termination)
        self.assertTrue(trace.encountered_errors)
        self.assertGreater(len(trace.replanning_actions_taken), 0)
        self.assertIsNotNone(trace.final_itinerary)
        self.assertTrue(trace.final_itinerary.budget_summary.within_budget)


if __name__ == "__main__":
    unittest.main()
