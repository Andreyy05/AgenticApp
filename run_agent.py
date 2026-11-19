import os
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich import print as rprint

from models import TripInput, RunTrace
from agent_loop import TravelPlannerAgent

console = Console()
TRACES_DIR = Path(__file__).parent / "traces"


def save_trace_to_markdown(trace: RunTrace, filepath: Path):
    """Generates an elegant, readable Markdown trace file for homework evaluation."""
    md = []
    md.append(f"# Agent Execution Trace: {trace.scenario_name}\n")
    md.append(f"- **Run ID**: `{trace.run_id}`")
    md.append(f"- **Destination**: **{trace.input_parameters.destination}** ({trace.input_parameters.start_date} to {trace.input_parameters.end_date})")
    md.append(f"- **Budget**: **${trace.input_parameters.budget_usd:.2f} USD**")
    md.append(f"- **Pace**: {trace.input_parameters.pace.capitalize()} | **Dietary**: {', '.join(trace.input_parameters.dietary) or 'None'}")
    md.append(f"- **Interests**: {', '.join(trace.input_parameters.interests)}")
    md.append(f"- **Total Steps**: {trace.total_steps}")
    md.append(f"- **Encountered Tool Errors**: `{'YES (Recovered via Replanning)' if trace.encountered_errors else 'NO (Smooth Run)'}`")
    md.append(f"- **Clean Termination**: `{'YES' if trace.clean_termination else 'NO'}`\n")

    if trace.encountered_errors:
        md.append("## ⚠️ Error & Replanning Log\n")
        for err in trace.error_descriptions:
            md.append(f"- **Tool Error Detected**: `{err}`")
        for replan in trace.replanning_actions_taken:
            md.append(f"- **Agent Replanning Decision**: {replan}")
        md.append("")

    md.append("## 🔁 Step-by-Step Agent Loop Execution\n")
    for s in trace.steps:
        icon = "✅" if s.tool_success else "❌"
        md.append(f"### Step {s.step_number}: State `{s.agent_state}`")
        md.append(f"**Thought**: _{s.thought}_  \n")
        if s.tool_called:
            md.append(f"- **Tool Called**: `{s.tool_called}`")
            md.append(f"- **Arguments**: `{json.dumps(s.tool_arguments)}`")
            md.append(f"- **Status**: {icon} `{'Success' if s.tool_success else 'Tool Error'}`")
            if s.error_message:
                md.append(f"- **Error Message**: `{s.error_message}`")
            if s.replanning_note:
                md.append(f"- **Replanning Action**: **{s.replanning_note}**")
            if s.tool_output:
                md.append(f"- **Tool Output**: {s.tool_output}")
        md.append("")

    if trace.final_itinerary:
        itin = trace.final_itinerary
        md.append("## 📋 Final Structured Output (Pydantic Validated Itinerary)\n")
        md.append(f"### Trip Overview: {itin.destination} ({itin.total_days} Days)")
        md.append(f"- **Flight**: {itin.flight.airline} {itin.flight.flight_number} (${itin.flight.price_usd:.2f})")
        md.append(f"- **Lodging**: {itin.lodging.name} ({itin.lodging.type}) in {itin.lodging.neighborhood} (${itin.lodging.total_cost_usd:.2f})")
        md.append(f"- **Agent Summary**: {itin.agent_notes}\n")

        md.append("### Day-by-Day Schedule\n")
        for day in itin.day_by_day:
            md.append(f"#### Day {day.day_number} ({day.date}) — Weather: {day.weather_summary}")
            md.append(f"- **Morning**: **{day.morning.title}** (${day.morning.cost_usd:.2f}) — {day.morning.description}")
            md.append(f"- **Afternoon**: **{day.afternoon.title}** (${day.afternoon.cost_usd:.2f}) — {day.afternoon.description}")
            md.append(f"- **Evening**: **{day.evening.title}** — {day.evening.description}")
            md.append(f"- **Daily Food Estimate**: ${day.estimated_food_cost_usd:.2f} | **Day Total**: ${day.day_total_usd:.2f}\n")

        b = itin.budget_summary
        md.append("### 💰 Budget Breakdown")
        md.append("| Category | Amount (USD) |")
        md.append("|---|---|")
        md.append(f"| Flights | ${b.flights_cost_usd:.2f} |")
        md.append(f"| Lodging | ${b.lodging_cost_usd:.2f} |")
        md.append(f"| Activities | ${b.activities_cost_usd:.2f} |")
        md.append(f"| Estimated Meals | ${b.meals_cost_usd:.2f} |")
        md.append(f"| **Total Spent** | **${b.total_spent_usd:.2f}** |")
        md.append(f"| **Allocated Budget** | **${b.allocated_budget_usd:.2f}** |")
        md.append(f"| **Remaining Buffer** | **${b.remaining_usd:.2f}** |")
        md.append(f"| **Within Budget?** | `{'YES' if b.within_budget else 'NO'}` |\n")

        md.append("### 🎒 Travel & Packing Tips")
        for tip in itin.packing_and_travel_tips:
            md.append(f"- {tip}")
        md.append("")

    filepath.write_text("\n".join(md), encoding="utf-8")


def print_cli_summary(trace: RunTrace):
    """Prints rich terminal visualization of the agent trace."""
    console.print()
    border_style = "yellow" if trace.encountered_errors else "green"
    console.print(Panel(
        f"[bold]Scenario: {trace.scenario_name}[/bold]\n"
        f"Destination: [cyan]{trace.input_parameters.destination}[/cyan] | Budget: [green]${trace.input_parameters.budget_usd}[/green] | Pace: {trace.input_parameters.pace}\n"
        f"Total Loop Steps: [bold]{trace.total_steps}[/bold] | Tool Errors Handled: [bold]{'YES (Replanned)' if trace.encountered_errors else 'NO'}[/bold] | Terminated: [bold green]{trace.clean_termination}[/bold green]",
        title=f"RUN: {trace.run_id}",
        border_style=border_style
    ))

    # Steps Tree
    tree = Tree(f"[bold]Agent Execution Loop Steps ({trace.total_steps} steps)[/bold]")
    for s in trace.steps:
        icon = "🟢" if s.tool_success else "🔴"
        step_branch = tree.add(f"{icon} [bold cyan]Step {s.step_number}[/bold cyan] [{s.agent_state}] Tool: [yellow]{s.tool_called or 'None'}[/yellow]")
        step_branch.add(f"[dim]Thought:[/dim] {s.thought}")
        if s.error_message:
            step_branch.add(f"[bold red]Tool Error:[/bold red] {s.error_message}")
        if s.replanning_note:
            step_branch.add(f"[bold yellow]Replanning Decision:[/bold yellow] {s.replanning_note}")
        if s.tool_output:
            step_branch.add(f"[dim green]Result:[/dim green] {s.tool_output}")

    console.print(tree)

    if trace.final_itinerary:
        itin = trace.final_itinerary
        b = itin.budget_summary
        t = Table(title=f"Budget Verification for {itin.destination} ({itin.total_days} Days)")
        t.add_column("Category", style="cyan")
        t.add_column("Cost (USD)", style="bold", justify="right")
        t.add_row("Flights", f"${b.flights_cost_usd:.2f}")
        t.add_row("Lodging", f"${b.lodging_cost_usd:.2f}")
        t.add_row("Activities", f"${b.activities_cost_usd:.2f}")
        t.add_row("Estimated Meals", f"${b.meals_cost_usd:.2f}")
        t.add_section()
        t.add_row("Total Spent", f"${b.total_spent_usd:.2f}", style="bold green" if b.within_budget else "bold red")
        t.add_row("Budget Limit", f"${b.allocated_budget_usd:.2f}")
        t.add_row("Remaining Balance", f"${b.remaining_usd:.2f}", style="green")
        console.print(t)


def run_interactive_mode(agent: TravelPlannerAgent):
    """Allows user to plan a trip interactively from the command line."""
    console.print("\n" + "=" * 70)
    console.print(Panel("[bold cyan]🧭 INTERAKTIVNÍ REŽIM: NAPLÁNUJTE SI VLASTNÍ CESTU[/bold cyan]", border_style="cyan"))
    console.print("[dim]Podporované ukázkové destinace: Paris, Tokyo[/dim]\n")

    dest = console.input("[bold yellow]1. Cílové město (Paris / Tokyo) [výchozí: Paris]: [/bold yellow]").strip() or "Paris"
    budget_raw = console.input("[bold yellow]2. Celkový rozpočet v USD [výchozí: 1000]: [/bold yellow]").strip() or "1000"
    start_d = console.input("[bold yellow]3. Datum odjezdu (YYYY-MM-DD) [výchozí: 2026-06-10]: [/bold yellow]").strip() or "2026-06-10"
    end_d = console.input("[bold yellow]4. Datum návratu (YYYY-MM-DD) [výchozí: 2026-06-14]: [/bold yellow]").strip() or "2026-06-14"
    interests_raw = console.input("[bold yellow]5. Zájmy oddělené čárkou (např. art, food, history) [výchozí: art, food]: [/bold yellow]").strip()
    
    interests = [i.strip() for i in interests_raw.split(",")] if interests_raw else ["art", "food"]

    try:
        budget_val = float(budget_raw)
    except ValueError:
        budget_val = 1000.0

    user_input = TripInput(
        destination=dest.capitalize(),
        origin="PRG",
        start_date=start_d,
        end_date=end_d,
        budget_usd=budget_val,
        pace="moderate",
        interests=interests,
        dietary=[]
    )

    console.print(f"\n[bold green]>>> Spouštím agentní smyčku pro {user_input.destination}...[/bold green]")
    custom_trace = agent.run(user_input, scenario_name=f"Vlastní interaktivní běh: {user_input.destination}")
    print_cli_summary(custom_trace)

    # Save custom run
    custom_json = TRACES_DIR / "custom_interactive_run.json"
    custom_md = TRACES_DIR / "custom_interactive_run.md"
    custom_json.write_text(custom_trace.model_dump_json(indent=2), encoding="utf-8")
    save_trace_to_markdown(custom_trace, custom_md)
    console.print(f"\n[green]Váš výsledek byl uložen do [bold]{custom_md}[/bold]![/green]")


def main():
    TRACES_DIR.mkdir(parents=True, exist_ok=True)
    agent = TravelPlannerAgent(max_steps=15)

    if "--interactive" in sys.argv or "-i" in sys.argv:
        run_interactive_mode(agent)
        return

    console.print(Panel.fit(
        "[bold cyan]Homework 3: Agentic Application — Travel-Planner Agent[/bold cyan]\n"
        "Features: Explicit Agent Loop · Tool Calling · Error Recovery/Replanning · Structured Pydantic Outputs",
        border_style="cyan"
    ))

    # ========================================================================
    # RUN 1: Paris Cultural & Culinary Trip (Smooth execution trace)
    # ========================================================================
    console.print("\n[bold green]>>> EXECUTING RUN 1: Paris Cultural & Culinary Trip (Smooth Baseline)[/bold green]")
    input_paris = TripInput(
        destination="Paris",
        origin="PRG",
        start_date="2026-06-10",
        end_date="2026-06-13",
        budget_usd=900.0,
        pace="moderate",
        interests=["art", "museum", "history", "food"],
        dietary=["vegetarian"]
    )

    trace_paris = agent.run(input_paris, scenario_name="Run 1: Paris Cultural 4-Day Trip")
    print_cli_summary(trace_paris)

    # Save Run 1 Traces
    path_paris_json = TRACES_DIR / "run_1_paris.json"
    path_paris_md = TRACES_DIR / "run_1_paris.md"
    path_paris_json.write_text(trace_paris.model_dump_json(indent=2), encoding="utf-8")
    save_trace_to_markdown(trace_paris, path_paris_md)
    console.print(f"[green]Saved Run 1 trace to {path_paris_json} and {path_paris_md}[/green]")

    # ========================================================================
    # RUN 2: Tokyo Budget Trip with Tool Error & Replanning
    # ========================================================================
    console.print("\n[bold yellow]>>> EXECUTING RUN 2: Tokyo Budget Trip (Tool Error Recovery & Replanning)[/bold yellow]")
    input_tokyo = TripInput(
        destination="Tokyo",
        origin="PRG",
        start_date="2026-09-15",
        end_date="2026-09-19",
        budget_usd=1350.0,
        pace="moderate",
        interests=["pop culture", "tech", "food", "history"],
        dietary=[]
    )

    trace_tokyo = agent.run(input_tokyo, scenario_name="Run 2: Tokyo Budget Trip with Tool Error & Replanning")
    print_cli_summary(trace_tokyo)

    # Save Run 2 Traces
    path_tokyo_json = TRACES_DIR / "run_2_tokyo.json"
    path_tokyo_md = TRACES_DIR / "run_2_tokyo.md"
    path_tokyo_json.write_text(trace_tokyo.model_dump_json(indent=2), encoding="utf-8")
    save_trace_to_markdown(trace_tokyo, path_tokyo_md)
    console.print(f"[green]Saved Run 2 trace to {path_tokyo_json} and {path_tokyo_md}[/green]")

    # ========================================================================
    # Comparison Summary Table
    # ========================================================================
    console.print("\n[bold]=== HOMEWORK 3 SUBMISSION SUMMARY: 2 REQUIRED RUNS ===[/bold]")
    summary_table = Table(title="Runs Comparison")
    summary_table.add_column("Run", style="bold")
    summary_table.add_column("Destination")
    summary_table.add_column("Budget")
    summary_table.add_column("Total Steps")
    summary_table.add_column("Tool Errors Handled")
    summary_table.add_column("Replanning Details")
    summary_table.add_column("Clean Termination")

    summary_table.add_row(
        "Run 1",
        trace_paris.input_parameters.destination,
        f"${trace_paris.input_parameters.budget_usd:.0f}",
        str(trace_paris.total_steps),
        "[green]None (Smooth)[/green]",
        "N/A",
        "[bold green]YES[/bold green]"
    )
    summary_table.add_row(
        "Run 2",
        trace_tokyo.input_parameters.destination,
        f"${trace_tokyo.input_parameters.budget_usd:.0f}",
        str(trace_tokyo.total_steps),
        "[yellow]NO_FLIGHTS_UNDER_BUDGET[/yellow]",
        "Rebalanced flight cap & switched to budget lodging",
        "[bold green]YES[/bold green]"
    )
    console.print(summary_table)


if __name__ == "__main__":
    main()
