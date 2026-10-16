"""Temporary command-line smoke test for the PawPal+ scheduling classes."""

from pawpal_system import CareTask, Owner, Pet, Scheduler


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=90)
    mochi = Pet(name="Mochi", species="cat", age=3)
    biscuit = Pet(name="Biscuit", species="dog", age=5)
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    mochi.add_task(
        CareTask(
            title="Breakfast",
            duration_minutes=10,
            priority="medium",
            preferred_time="08:00",
        )
    )
    biscuit.add_task(
        CareTask(
            title="Morning walk",
            duration_minutes=30,
            priority="medium",
            preferred_time="08:30",
        )
    )
    biscuit.add_task(
        CareTask(
            title="Dinner",
            duration_minutes=15,
            priority="medium",
            preferred_time="18:00",
        )
    )

    schedule = Scheduler(owner).generate_schedule()
    print("Today's Schedule")
    print(schedule.explain_plan())


if __name__ == "__main__":
    main()