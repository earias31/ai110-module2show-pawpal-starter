from datetime import date

import streamlit as st
from pawpal_system import CareTask, Owner, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    st.session_state["owner"] = Owner()

st.title("🐾 PawPal+")

st.markdown(
    """
Plan your pet's care tasks and build a daily schedule based on priority and available time.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

PawPal+ uses your saved owner, pet, and care-task details to create a daily plan.
"""
    )

with st.expander("How PawPal+ works", expanded=True):
    st.markdown(
        """
Add pets and care tasks, then generate a daily plan that prioritizes tasks within your available time.
"""
    )

st.divider()

owner = st.session_state["owner"]
owner.name = st.text_input("Owner name", value=owner.name or "Jordan")

st.divider()
st.subheader("Add a Pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    pet_age = st.number_input("Age (years)", min_value=0, max_value=100, value=1)
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    pet = Pet()
    pet.update_information(pet_name.strip(), species, int(pet_age))
    owner.add_pet(pet)
    st.success(f"Added {pet.name} to {owner.name}'s pets.")

if owner.pets:
    st.write("Your pets:")
    st.table(
        [{"Name": pet.name, "Species": pet.species, "Age": pet.age} for pet in owner.pets]
    )
else:
    st.info("Add a pet to get started. You can also create household tasks without assigning a pet.")

st.divider()
st.subheader("Add a Care Task")
pet_choices = [-1, *range(len(owner.pets))]
with st.form("add_task_form"):
    task_title = st.text_input("Task title", value="Morning walk")
    task_duration = st.number_input(
        "Duration (minutes)", min_value=1, max_value=240, value=20
    )
    task_priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    task_time = st.text_input("Preferred time (optional)", value="")
    task_recurrence = st.selectbox("Repeats", ["once", "daily", "weekly"])
    task_pet_index = st.selectbox(
        "Assign to",
        pet_choices,
        format_func=lambda index: "Household" if index == -1 else owner.pets[index].name,
    )
    add_task = st.form_submit_button("Add task")

if add_task:
    try:
        task = CareTask(
            title=task_title.strip(),
            duration_minutes=int(task_duration),
            priority=task_priority,
            preferred_time=task_time.strip(),
            recurrence=task_recurrence,
        )
    except ValueError as error:
        st.error(f"Could not add task: {error}")
    else:
        if task_pet_index == -1:
            owner.tasks.append(task)
        else:
            owner.pets[task_pet_index].add_task(task)
        st.success(f"Added task: {task.title}.")

tasks = owner.get_all_tasks()
if tasks:
    st.write("Current tasks:")
    pet_filter = st.selectbox(
        "Filter by pet",
        [-1, *range(len(owner.pets))],
        format_func=lambda index: "All pets" if index == -1 else owner.pets[index].name,
    )
    status_filter = st.selectbox(
        "Filter by status",
        ["All statuses", "pending", "accepted", "completed", "denied"],
    )
    visible_tasks = Scheduler(owner).filter_tasks(
        pet=None if pet_filter == -1 else owner.pets[pet_filter],
        status=None if status_filter == "All statuses" else status_filter,
    )
    st.table(
        [
            {
                "Task": task.title,
                "Pet": task.pet.name if task.pet is not None else "Household",
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority,
                "Status": task.status,
                "Repeats": task.recurrence,
            }
            for task in visible_tasks
        ]
    )

    incomplete_tasks = [
        task for task in tasks if task.status in {"pending", "accepted"}
    ]
    if incomplete_tasks:
        st.subheader("Mark a Task Complete")
        task_to_complete = st.selectbox(
            "Task",
            incomplete_tasks,
            format_func=lambda task: (
                f"{task.title} ({task.pet.name if task.pet is not None else 'Household'})"
            ),
            key="task_to_complete",
        )
        if st.button("Mark complete"):
            next_task = Scheduler(owner).mark_task_complete(task_to_complete)
            if next_task is None:
                st.success(f"Completed {task_to_complete.title}.")
            else:
                st.success(
                    f"Completed {task_to_complete.title}; next occurrence is due "
                    f"{next_task.recurrence_start_date.isoformat()}."
                )
else:
    st.info("No tasks yet. Add one above.")

st.divider()
st.subheader("Build Schedule")
schedule_date = st.date_input("Schedule date", value=date.today())
available_minutes = st.number_input(
    "Available care time (minutes)", min_value=0, max_value=1440, value=90
)

if st.button("Generate schedule"):
    owner.set_available_time(int(available_minutes))
    selected_pet = None if not tasks or pet_filter == -1 else owner.pets[pet_filter]
    selected_status = (
        None if not tasks or status_filter == "All statuses" else status_filter
    )
    schedule = Scheduler(owner).generate_schedule(
        schedule_date=schedule_date,
        pet=selected_pet,
        status=selected_status,
    )
    st.markdown(schedule.explain_plan())
