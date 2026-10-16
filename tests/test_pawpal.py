from pawpal_system import CareTask, Pet


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
