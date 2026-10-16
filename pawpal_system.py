"""Backend data models and scheduling logic for PawPal+."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Owner:
    """An owner, their availability, preferences, pets, and care tasks."""

    name: str = ""
    available_minutes: int = 0
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)
    tasks: list[CareTask] = field(default_factory=list)

    def update_preferences(self, preferences: list[str]) -> None:
        """Replace the owner's scheduling preferences."""
        self.preferences = list(preferences)

    def set_available_time(self, minutes: int) -> None:
        """Set the owner's available daily minutes."""
        if minutes < 0:
            raise ValueError("Available minutes cannot be negative.")
        self.available_minutes = minutes

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's household if it is not already present."""
        if all(existing is not pet for existing in self.pets):
            self.pets.append(pet)

    def get_all_tasks(self) -> list[CareTask]:
        """Return household tasks, including tasks attached to individual pets."""
        combined: list[CareTask] = []
        for task in [*self.tasks, *(task for pet in self.pets for task in pet.tasks)]:
            if all(existing is not task for existing in combined):
                combined.append(task)
        return combined


@dataclass
class Pet:
    """A pet and its care needs and assigned tasks."""

    name: str = ""
    species: str = ""
    age: int = 0
    care_needs: list[str] = field(default_factory=list)
    tasks: list[CareTask] = field(default_factory=list)

    def update_information(self, name: str, species: str, age: int) -> None:
        """Update the pet's basic information."""
        if age < 0:
            raise ValueError("Pet age cannot be negative.")
        self.name = name
        self.species = species
        self.age = age

    def add_care_need(self, need: str) -> None:
        """Add a non-empty care need once."""
        cleaned_need = need.strip()
        if not cleaned_need:
            raise ValueError("Care need cannot be empty.")
        if cleaned_need not in self.care_needs:
            self.care_needs.append(cleaned_need)

    def add_task(self, task: CareTask) -> None:
        """Assign a task to this pet and record the pet on the task."""
        if task.pet is not None and task.pet is not self:
            raise ValueError("This task is already assigned to another pet.")
        if all(existing is not task for existing in self.tasks):
            self.tasks.append(task)
        task.pet = self


@dataclass
class CareTask:
    """A care activity with duration, priority, status, and optional pet."""

    title: str = ""
    description: str = ""
    duration_minutes: int = 0
    priority: str = "medium"
    preferred_time: str = ""
    status: str = "pending"
    suggestion_reason: str = ""
    pet: Optional[Pet] = None

    def __post_init__(self) -> None:
        """Validate the task's duration and priority after initialization."""
        self._validate_duration(self.duration_minutes)
        self._validate_priority(self.priority)

    @staticmethod
    def _validate_duration(duration_minutes: int) -> None:
        """Reject task durations below zero."""
        if duration_minutes < 0:
            raise ValueError("Task duration cannot be negative.")

    @staticmethod
    def _validate_priority(priority: str) -> None:
        """Reject priorities outside the supported levels."""
        if priority.lower() not in {"low", "medium", "high"}:
            raise ValueError("Priority must be 'low', 'medium', or 'high'.")

    def update_details(
        self,
        title: str,
        duration_minutes: int,
        priority: str,
    ) -> None:
        """Update the task's title, duration, and priority."""
        self._validate_duration(duration_minutes)
        self._validate_priority(priority)
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority.lower()

    def accept_suggestion(self) -> None:
        """Mark a suggested task as accepted for scheduling."""
        self.status = "accepted"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.status = "completed"

    def mark_denied(self) -> None:
        """Mark a suggested task as denied so it is excluded from schedules."""
        self.status = "denied"


@dataclass
class DailySchedule:
    """The tasks selected for one day and their total time cost."""

    schedule_date: date = field(default_factory=date.today)
    available_minutes: int = 0
    scheduled_tasks: list[CareTask] = field(default_factory=list)
    total_minutes: int = 0

    def __post_init__(self) -> None:
        """Validate the time budget and calculate the scheduled total."""
        if self.available_minutes < 0:
            raise ValueError("Available minutes cannot be negative.")
        self.total_minutes = sum(task.duration_minutes for task in self.scheduled_tasks)

    def add_task(self, task: CareTask) -> None:
        """Add a task if it fits in the remaining available time."""
        if any(existing is task for existing in self.scheduled_tasks):
            return
        if self.total_minutes + task.duration_minutes > self.available_minutes:
            raise ValueError("Task exceeds the schedule's remaining available time.")
        self.scheduled_tasks.append(task)
        self.total_minutes += task.duration_minutes

    def remove_task(self, task: CareTask) -> bool:
        """Remove a scheduled task and return whether it was present."""
        for index, existing in enumerate(self.scheduled_tasks):
            if existing is task:
                del self.scheduled_tasks[index]
                self.total_minutes -= task.duration_minutes
                return True
        return False

    def explain_plan(self) -> str:
        """Describe scheduled tasks and how much time remains."""
        lines = [f"Daily plan for {self.schedule_date.isoformat()}:"]
        if not self.scheduled_tasks:
            lines.append("No tasks fit the available schedule.")
        for task in self.scheduled_tasks:
            pet_name = f" ({task.pet.name})" if task.pet is not None else ""
            time = f" at {task.preferred_time}" if task.preferred_time else ""
            lines.append(
                f"- {task.title or task.description}{pet_name}{time} "
                f"— {task.duration_minutes} min, {task.priority} priority"
            )
        lines.append(
            f"Total: {self.total_minutes}/{self.available_minutes} minutes."
        )
        return "\n".join(lines)


class Scheduler:
    """Rank, filter, and schedule care tasks across an owner's pets."""

    def __init__(
        self,
        owner: Owner,
        pets: Optional[list[Pet]] = None,
        tasks: Optional[list[CareTask]] = None,
    ) -> None:
        """Initialize scheduling from the owner's pets and tasks."""
        self.owner = owner
        self.pets = list(owner.pets if pets is None else pets)
        for pet in self.pets:
            owner.add_pet(pet)
        self.tasks = list(owner.get_all_tasks() if tasks is None else tasks)

    def generate_schedule(
        self,
        schedule_date: Optional[date] = None,
        available_minutes: Optional[int] = None,
    ) -> DailySchedule:
        """Build a schedule using the given or owner's default time budget."""
        budget = (
            self.owner.available_minutes
            if available_minutes is None
            else available_minutes
        )
        if budget < 0:
            raise ValueError("Available minutes cannot be negative.")
        schedule = DailySchedule(
            schedule_date=date.today() if schedule_date is None else schedule_date,
            available_minutes=budget,
        )
        for task in self.filter_tasks_by_available_time(self.rank_tasks(), budget):
            schedule.add_task(task)
        return schedule

    def rank_tasks(self) -> list[CareTask]:
        """Return eligible tasks by priority, preferred time, then duration."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        tasks = [task for task in self.tasks if task.status not in {"completed", "denied"}]
        return sorted(
            tasks,
            key=lambda task: (
                priority_order[task.priority.lower()],
                not bool(task.preferred_time),
                task.preferred_time.casefold(),
                task.duration_minutes,
            ),
        )

    def filter_tasks_by_available_time(
        self,
        tasks: list[CareTask],
        available_minutes: Optional[int] = None,
    ) -> list[CareTask]:
        """Choose ranked tasks that fit within the available time budget."""
        budget = (
            self.owner.available_minutes
            if available_minutes is None
            else available_minutes
        )
        if budget < 0:
            raise ValueError("Available minutes cannot be negative.")
        selected: list[CareTask] = []
        remaining = budget
        for task in tasks:
            if task.duration_minutes <= remaining:
                selected.append(task)
                remaining -= task.duration_minutes
        return selected