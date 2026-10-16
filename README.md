# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Terminal output from running `python main.py`:

```
Today's Schedule
Daily plan for 2026-10-16:
- Breakfast (Mochi) at 08:00 — 10 min, medium priority
- Morning walk (Biscuit) at 08:30 — 30 min, medium priority
- Dinner (Biscuit) at 18:00 — 15 min, medium priority
Total: 55/90 minutes.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

The scheduler keeps the demo's simple, deterministic behavior while adding a few
useful safeguards for everyday planning. Preferred times use 24-hour `HH:MM`
format; weekly tasks repeat on the weekday of their start date. A completed
recurring task becomes eligible again at its next occurrence.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting | `Scheduler.sort_by_time()` and `Scheduler.rank_tasks()` | `sort_by_time()` orders preferred `HH:MM` times chronologically and puts untimed tasks last. `rank_tasks()` sorts eligible tasks by time, then priority, duration, and title. |
| Filtering | `Scheduler.filter_tasks()` and `Scheduler.generate_schedule()` | Filter by pet object, pet name, or status. Schedule generation excludes denied tasks, completed one-time tasks, and recurring tasks that are not due on the requested date. |
| Time budget | `Scheduler.filter_tasks_by_available_time()` and `Scheduler.generate_schedule()` | Greedily selects ranked tasks that fit the available minutes. |
| Conflict detection and warnings | `Scheduler.detect_conflicts()`, `Scheduler.get_conflict_warnings()`, and `Scheduler.generate_schedule()` | Detects overlaps between positive-duration timed tasks, whether they belong to the same pet or different pets. The warning method returns readable messages instead of raising an error; schedule generation skips later overlaps and explains skipped tasks. |
| Recurring tasks | `CareTask.is_due_on()`, `CareTask.create_next_occurrence()`, and `Scheduler.mark_task_complete()` | Daily tasks are due again the next day; weekly tasks repeat on the weekday of their start date. Completing a recurring task creates a fresh pending occurrence. |

The standalone `main.py` is intentionally a fixed-data smoke demo, so its owner,
pets, and sample tasks still need to be edited in code. The Streamlit app exposes
task recurrence, schedule date, and pet/status filters for interactive use.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
