"""Temporary command-line smoke test for the PawPal+ scheduling classes."""

from pawpal_system import CareTask, Owner, Pet, Scheduler


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=90)
    mochi = Pet(name="Mochi", species="cat", age=3)
    biscuit = Pet(name="Biscuit", species="dog", age=5)
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    dinner = CareTask(
        title="Dinner",
        duration_minutes=15,
        priority="medium",
        preferred_time="18:00",
    )
    breakfast = CareTask(
        title="Breakfast",
        duration_minutes=10,
        priority="medium",
        preferred_time="08:00",
    )
    morning_walk = CareTask(
        title="Morning walk",
        duration_minutes=30,
        priority="medium",
        preferred_time="08:30",
    )
    evening_medicine = CareTask(
        title="Evening medicine",
        duration_minutes=5,
        priority="high",
        preferred_time="18:00",
    )
    completed_brushing = CareTask(
        title="Brush teeth",
        duration_minutes=5,
        priority="low",
        preferred_time="07:30",
    )
    completed_brushing.mark_complete()

    # Add tasks out of time order to demonstrate the scheduler's sort.
    biscuit.add_task(dinner)
    mochi.add_task(breakfast)
    biscuit.add_task(morning_walk)
    mochi.add_task(evening_medicine)
    mochi.add_task(completed_brushing)

    scheduler = Scheduler(owner)
    print("Tasks sorted by preferred time:")
    for task in scheduler.sort_by_time():
        pet_name = task.pet.name if task.pet is not None else "Household"
        print(f"- {task.preferred_time} {task.title} ({pet_name}; {task.status})")

    print("\nTasks for Biscuit:")
    biscuit_tasks = scheduler.sort_by_time(
        scheduler.filter_tasks(pet_name="Biscuit")
    )
    for task in biscuit_tasks:
        print(f"- {task.preferred_time} {task.title}")

    print("\nCompleted tasks:")
    completed_tasks = scheduler.sort_by_time(
        scheduler.filter_tasks(status="completed")
    )
    for task in completed_tasks:
        print(f"- {task.title}")

    print("\nScheduling warnings:")
    warnings = scheduler.get_conflict_warnings()
    if warnings:
        for warning in warnings:
            print(warning)
    else:
        print("No scheduling conflicts detected.")

    schedule = scheduler.generate_schedule()
    print("Today's Schedule")
    print(schedule.explain_plan())


if __name__ == "__main__":
    main()