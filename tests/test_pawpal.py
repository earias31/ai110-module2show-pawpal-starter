from datetime import date, timedelta

import pytest

from pawpal_system import CareTask, Owner, Pet, Scheduler


def test_mark_complete_changes_task_status() -> None:
    task = CareTask(title="Feed the cat")

    task.mark_complete()

    assert task.status == "completed"


def test_adding_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="cat")
    task = CareTask(title="Feed Mochi")
    initial_task_count = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == initial_task_count + 1


def test_scheduler_sorts_by_time_before_priority() -> None:
    later_high_priority = CareTask(
        title="Evening medicine", preferred_time="18:00", priority="high"
    )
    earlier_low_priority = CareTask(
        title="Breakfast", preferred_time="08:00", priority="low"
    )
    scheduler = Scheduler(Owner(), tasks=[later_high_priority, earlier_low_priority])

    assert scheduler.rank_tasks() == [earlier_low_priority, later_high_priority]


def test_filter_tasks_by_pet_and_status() -> None:
    mochi = Pet(name="Mochi")
    biscuit = Pet(name="Biscuit")
    pending = CareTask(title="Feed Mochi")
    mochi.add_task(pending)
    denied = CareTask(title="Walk Biscuit", status="denied")
    biscuit.add_task(denied)
    scheduler = Scheduler(Owner(), pets=[mochi, biscuit])

    assert scheduler.filter_tasks(pet=mochi) == [pending]
    assert scheduler.filter_tasks(status="denied") == [denied]
    assert scheduler.filter_tasks(pet=biscuit, status="pending") == []


def test_sort_by_time_orders_hh_mm_and_places_untimed_tasks_last() -> None:
    evening = CareTask(title="Dinner", preferred_time="18:00")
    morning = CareTask(title="Breakfast", preferred_time="08:00")
    untimed = CareTask(title="Play")
    scheduler = Scheduler(Owner(), tasks=[evening, untimed, morning])

    assert scheduler.sort_by_time() == [morning, evening, untimed]


def test_filter_tasks_by_pet_name_and_completion_status() -> None:
    mochi = Pet(name="Mochi")
    biscuit = Pet(name="Biscuit")
    mochi_task = CareTask(title="Feed Mochi")
    biscuit_task = CareTask(title="Walk Biscuit")
    biscuit_task.mark_complete()
    mochi.add_task(mochi_task)
    biscuit.add_task(biscuit_task)
    scheduler = Scheduler(Owner(), pets=[mochi, biscuit])

    assert scheduler.filter_tasks(pet_name="bIScUit") == [biscuit_task]
    assert scheduler.filter_tasks(status="completed") == [biscuit_task]


def test_recurring_tasks_are_due_on_their_repeat_dates() -> None:
    monday = date(2026, 10, 12)
    tuesday = monday + timedelta(days=1)
    daily = CareTask(
        title="Daily food",
        recurrence="daily",
        recurrence_start_date=monday,
    )
    weekly = CareTask(
        title="Weekly grooming",
        recurrence="weekly",
        recurrence_start_date=monday,
    )
    scheduler = Scheduler(Owner(), tasks=[daily, weekly])

    assert scheduler.rank_tasks(schedule_date=tuesday) == [daily]
    next_daily = scheduler.mark_task_complete(daily, tuesday)
    assert next_daily is not None
    assert next_daily is not daily
    assert next_daily.status == "pending"
    assert next_daily.recurrence_start_date == tuesday + timedelta(days=1)
    assert scheduler.rank_tasks(schedule_date=tuesday) == []
    assert scheduler.rank_tasks(schedule_date=tuesday + timedelta(days=1)) == [
        next_daily
    ]

    next_weekly = scheduler.mark_task_complete(weekly, monday)
    assert next_weekly is not None
    assert next_weekly.recurrence_start_date == monday + timedelta(days=7)
    assert next_weekly in scheduler.tasks
    assert next_weekly in scheduler.rank_tasks(schedule_date=monday + timedelta(days=7))


def test_completing_pet_recurring_task_registers_next_instance_on_pet() -> None:
    pet = Pet(name="Mochi")
    task = CareTask(title="Medication", recurrence="daily", pet=pet)
    pet.add_task(task)
    scheduler = Scheduler(Owner(), pets=[pet])

    next_task = scheduler.mark_task_complete(task, date(2026, 10, 16))

    assert next_task is not None
    assert next_task.pet is pet
    assert next_task in pet.tasks
    assert next_task in scheduler.tasks
    assert scheduler.mark_task_complete(task, date(2026, 10, 16)) is None


def test_daily_completion_defaults_next_due_date_to_tomorrow() -> None:
    today = date.today()
    task = CareTask(title="Daily feeding", recurrence="daily")
    scheduler = Scheduler(Owner(), tasks=[task])

    next_task = scheduler.mark_task_complete(task)

    assert next_task is not None
    assert next_task.recurrence_start_date == today + timedelta(days=1)


def test_completing_one_time_task_does_not_create_another_instance() -> None:
    task = CareTask(title="One-time vet visit")
    scheduler = Scheduler(Owner(), tasks=[task])

    assert scheduler.mark_task_complete(task, date(2026, 10, 16)) is None
    assert len(scheduler.tasks) == 1


def test_schedule_skips_overlapping_tasks_and_reports_conflict() -> None:
    breakfast = CareTask(title="Breakfast", preferred_time="08:00", duration_minutes=30)
    medicine = CareTask(title="Medicine", preferred_time="08:15", duration_minutes=5)
    walk = CareTask(title="Walk", preferred_time="09:00", duration_minutes=20)
    scheduler = Scheduler(Owner(), tasks=[walk, medicine, breakfast])

    schedule = scheduler.generate_schedule(available_minutes=90)

    assert schedule.scheduled_tasks == [breakfast, walk]
    assert schedule.conflicts == [(breakfast, medicine)]
    assert "Medicine overlaps with Breakfast" in schedule.explain_plan()
    assert scheduler.detect_conflicts() == [(breakfast, medicine)]


def test_conflict_warnings_cover_same_and_different_pets() -> None:
    mochi = Pet(name="Mochi")
    biscuit = Pet(name="Biscuit")
    mochi_feeding = CareTask(
        title="Mochi feeding", preferred_time="18:00", duration_minutes=10
    )
    mochi_medicine = CareTask(
        title="Mochi medicine", preferred_time="18:00", duration_minutes=5
    )
    biscuit_walk = CareTask(
        title="Biscuit walk", preferred_time="18:00", duration_minutes=20
    )
    mochi.add_task(mochi_feeding)
    mochi.add_task(mochi_medicine)
    biscuit.add_task(biscuit_walk)
    scheduler = Scheduler(Owner(), pets=[mochi, biscuit])

    warnings = scheduler.get_conflict_warnings()

    assert len(warnings) == 3
    assert all(warning.startswith("Warning:") for warning in warnings)
    assert all("both start at 18:00" in warning for warning in warnings)
    assert any("Mochi feeding (Mochi)" in warning for warning in warnings)
    assert any("Biscuit walk (Biscuit)" in warning for warning in warnings)


def test_conflict_warnings_are_empty_when_tasks_do_not_overlap() -> None:
    breakfast = CareTask(title="Breakfast", preferred_time="08:00", duration_minutes=10)
    walk = CareTask(title="Walk", preferred_time="08:10", duration_minutes=20)
    scheduler = Scheduler(Owner(), tasks=[breakfast, walk])

    assert scheduler.get_conflict_warnings() == []


def test_preferred_time_requires_24_hour_hh_mm_format() -> None:
    with pytest.raises(ValueError, match="HH:MM"):
        CareTask(title="Invalid time", preferred_time="8am")
