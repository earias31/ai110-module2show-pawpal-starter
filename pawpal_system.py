"""Backend data models and scheduling logic for PawPal+."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
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
    recurrence: str = "once"
    recurrence_start_date: date = field(default_factory=date.today)
    completed_dates: set[date] = field(default_factory=set)
    pet: Optional[Pet] = None

    def __post_init__(self) -> None:
        """Validate the task's duration and priority after initialization."""
        self._validate_duration(self.duration_minutes)
        self._validate_priority(self.priority)
        self.priority = self.priority.lower()
        self.status = self.status.lower()
        self.recurrence = self.recurrence.lower()
        self.preferred_time = self.preferred_time.strip()
        self._validate_preferred_time(self.preferred_time)
        self._validate_recurrence(self.recurrence)

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

    @staticmethod
    def _validate_preferred_time(preferred_time: str) -> None:
        """Accept an empty time or a 24-hour HH:MM time."""
        if not preferred_time:
            return
        parts = preferred_time.split(":")
        if (
            len(parts) != 2
            or any(not part.isdigit() for part in parts)
            or len(parts[0]) != 2
            or len(parts[1]) != 2
            or not 0 <= int(parts[0]) <= 23
            or not 0 <= int(parts[1]) <= 59
        ):
            raise ValueError("Preferred time must use 24-hour HH:MM format.")

    @staticmethod
    def _validate_recurrence(recurrence: str) -> None:
        """Reject recurrence values not supported by the scheduler."""
        if recurrence.lower() not in {"once", "daily", "weekly"}:
            raise ValueError("Recurrence must be 'once', 'daily', or 'weekly'.")

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

    def mark_complete(self, completed_on: Optional[date] = None) -> None:
        """Mark a task complete, recording the date for recurring tasks."""
        self.status = "completed"
        self.completed_dates.add(date.today() if completed_on is None else completed_on)

    def create_next_occurrence(self, completed_on: date) -> Optional[CareTask]:
        """Create a fresh pending task for the next daily or weekly occurrence."""
        if self.recurrence == "daily":
            next_date = completed_on + timedelta(days=1)
        elif self.recurrence == "weekly":
            days_until_next_weekday = (
                self.recurrence_start_date.weekday() - completed_on.weekday()
            ) % 7 or 7
            next_date = completed_on + timedelta(days=days_until_next_weekday)
        else:
            return None

        return CareTask(
            title=self.title,
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            preferred_time=self.preferred_time,
            status="pending",
            suggestion_reason=self.suggestion_reason,
            recurrence=self.recurrence,
            recurrence_start_date=next_date,
            pet=self.pet,
        )

    def is_due_on(self, schedule_date: date) -> bool:
        """Return whether this task has an unfinished occurrence on a date."""
        if self.status in {"completed", "denied"}:
            return False
        if schedule_date in self.completed_dates:
            return False
        if self.recurrence == "daily":
            return schedule_date >= self.recurrence_start_date
        if self.recurrence == "weekly":
            return (
                schedule_date >= self.recurrence_start_date
                and schedule_date.weekday() == self.recurrence_start_date.weekday()
            )
        return True

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
    conflicts: list[tuple[CareTask, CareTask]] = field(default_factory=list)

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
        if self.conflicts:
            lines.append("Skipped overlapping tasks:")
            for earlier, later in self.conflicts:
                lines.append(
                    f"- {later.title or later.description} overlaps with "
                    f"{earlier.title or earlier.description}."
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
        pet: Optional[Pet] = None,
        status: Optional[str] = None,
    ) -> DailySchedule:
        """Build a schedule using the given or owner's default time budget."""
        budget = (
            self.owner.available_minutes
            if available_minutes is None
            else available_minutes
        )
        if budget < 0:
            raise ValueError("Available minutes cannot be negative.")
        target_date = date.today() if schedule_date is None else schedule_date
        eligible_tasks = self.rank_tasks(pet, status, target_date)
        selected_tasks, conflicts = self._select_tasks(eligible_tasks, budget)
        schedule = DailySchedule(
            schedule_date=target_date,
            available_minutes=budget,
            conflicts=conflicts,
        )
        for task in selected_tasks:
            schedule.add_task(task)
        return schedule

    @staticmethod
    def _time_in_minutes(task: CareTask) -> Optional[int]:
        """Convert a validated preferred time into minutes after midnight."""
        if not task.preferred_time:
            return None
        hour, minute = (int(part) for part in task.preferred_time.split(":"))
        return hour * 60 + minute

    def filter_tasks(
        self,
        pet: Optional[Pet] = None,
        status: Optional[str] = None,
        pet_name: Optional[str] = None,
    ) -> list[CareTask]:
        """Filter tasks by pet, pet name, or status without changing task order."""
        if status is not None and status.lower() not in {
            "pending", "accepted", "completed", "denied"
        }:
            raise ValueError("Status must be pending, accepted, completed, or denied.")
        filtered = []
        for task in self.tasks:
            if pet is not None and task.pet is not pet:
                continue
            if (
                pet_name is not None
                and (
                    task.pet is None
                    or task.pet.name.casefold() != pet_name.strip().casefold()
                )
            ):
                continue
            if status is not None and task.status.lower() != status.lower():
                continue
            filtered.append(task)
        return filtered

    def mark_task_complete(
        self, task: CareTask, completed_on: Optional[date] = None
    ) -> Optional[CareTask]:
        """Complete a task and register a new instance for its next recurrence."""
        if task.status == "completed":
            return None

        completion_date = date.today() if completed_on is None else completed_on
        task.mark_complete(completion_date)
        next_task = task.create_next_occurrence(completion_date)
        if next_task is None:
            return None

        if task.pet is None:
            if all(existing is not next_task for existing in self.owner.tasks):
                self.owner.tasks.append(next_task)
        else:
            self.owner.add_pet(task.pet)
            task.pet.add_task(next_task)
        if all(existing is not next_task for existing in self.tasks):
            self.tasks.append(next_task)
        return next_task

    def sort_by_time(
        self, tasks: Optional[list[CareTask]] = None
    ) -> list[CareTask]:
        """Return tasks sorted by preferred HH:MM time, with untimed tasks last."""
        tasks_to_sort = self.tasks if tasks is None else tasks
        return sorted(
            tasks_to_sort,
            key=lambda task: (not bool(task.preferred_time), task.preferred_time),
        )

    def rank_tasks(
        self,
        pet: Optional[Pet] = None,
        status: Optional[str] = None,
        schedule_date: Optional[date] = None,
    ) -> list[CareTask]:
        """Return eligible tasks chronologically, then by priority and duration."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        target_date = date.today() if schedule_date is None else schedule_date
        tasks = []
        for task in self.filter_tasks(pet, status):
            if task.status == "denied":
                continue
            if status is not None and status.lower() not in {"pending", "accepted"}:
                continue
            if task.status == "completed" and task.recurrence == "once":
                continue
            if not task.is_due_on(target_date):
                continue
            tasks.append(task)
        return sorted(
            tasks,
            key=lambda task: (
                self._time_in_minutes(task) is None,
                self._time_in_minutes(task) or 0,
                priority_order[task.priority.lower()],
                task.duration_minutes,
                task.title.casefold(),
            ),
        )

    def detect_conflicts(
        self, tasks: Optional[list[CareTask]] = None
    ) -> list[tuple[CareTask, CareTask]]:
        """Return overlapping timed-task pairs using a sorted interval scan.

        The scan stops once later tasks start beyond the current task's end;
        zero-duration tasks do not produce conflicts.
        """
        timed_tasks = [
            (self._time_in_minutes(task), task)
            for task in (self.tasks if tasks is None else tasks)
            if self._time_in_minutes(task) is not None
        ]
        timed_tasks.sort(key=lambda item: item[0])
        conflicts: list[tuple[CareTask, CareTask]] = []
        for index, (start, task) in enumerate(timed_tasks):
            assert start is not None
            end = start + task.duration_minutes
            for later_start, later_task in timed_tasks[index + 1 :]:
                assert later_start is not None
                if later_start >= end:
                    break
                if task.duration_minutes > 0 and later_task.duration_minutes > 0:
                    conflicts.append((task, later_task))
        return conflicts

    def get_conflict_warnings(
        self, tasks: Optional[list[CareTask]] = None
    ) -> list[str]:
        """Format detected overlaps as readable warnings without changing tasks.

        Pet names are included when available; this method reports conflicts
        without rejecting tasks or interrupting schedule generation.
        """
        warnings = []
        for first, second in self.detect_conflicts(tasks):
            first_pet = f" ({first.pet.name})" if first.pet is not None else ""
            second_pet = f" ({second.pet.name})" if second.pet is not None else ""
            if first.preferred_time == second.preferred_time:
                detail = f"both start at {first.preferred_time}"
            else:
                detail = (
                    f"{first.preferred_time} and {second.preferred_time} "
                    "have overlapping durations"
                )
            warnings.append(
                f"Warning: {first.title or first.description}{first_pet} and "
                f"{second.title or second.description}{second_pet} conflict; {detail}."
            )
        return warnings

    def _select_tasks(
        self, tasks: list[CareTask], budget: int
    ) -> tuple[list[CareTask], list[tuple[CareTask, CareTask]]]:
        """Select tasks within the time budget, skipping later overlaps."""
        selected: list[CareTask] = []
        conflicts: list[tuple[CareTask, CareTask]] = []
        remaining = budget
        for task in tasks:
            if task.duration_minutes > remaining:
                continue
            task_start = self._time_in_minutes(task)
            overlapping = next(
                (
                    existing
                    for existing in selected
                    if task_start is not None
                    and (existing_start := self._time_in_minutes(existing)) is not None
                    and task.duration_minutes > 0
                    and existing.duration_minutes > 0
                    and task_start < existing_start + existing.duration_minutes
                    and existing_start < task_start + task.duration_minutes
                ),
                None,
            )
            if overlapping is not None:
                conflicts.append((overlapping, task))
                continue
            selected.append(task)
            remaining -= task.duration_minutes
        return selected, conflicts

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
        return self._select_tasks(tasks, budget)[0]