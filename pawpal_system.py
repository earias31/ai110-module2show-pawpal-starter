"""Core data models and class skeletons for the PawPal+ system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Owner:
    """Pet owner settings used when creating a care schedule."""

    name: str
    available_minutes: int = 0
    preferences: list[str] = field(default_factory=list)

    def update_preferences(self, preferences: list[str]) -> None:
        """Update the owner's scheduling preferences."""
        pass

    def set_available_time(self, minutes: int) -> None:
        """Set the amount of time available for pet care."""
        pass


@dataclass
class Pet:
    """Basic information and care needs for a pet."""

    name: str
    species: str
    age: Optional[int] = None
    care_needs: list[str] = field(default_factory=list)

    def update_information(
        self, name: str, species: str, age: Optional[int]
    ) -> None:
        """Update the pet's basic information."""
        pass

    def add_care_need(self, need: str) -> None:
        """Add a care need for this pet."""
        pass


@dataclass
class CareTask:
    """A pet-care task that can be considered for scheduling."""

    title: str
    duration_minutes: int
    priority: str
    description: str = ""
    preferred_time: Optional[str] = None
    status: str = "pending"

    def update_details(
        self, title: str, duration_minutes: int, priority: str
    ) -> None:
        """Update the task's details."""
        pass

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        pass

    def mark_denied(self) -> None:
        """Mark the task as denied by the owner."""
        pass


@dataclass
class TaskSuggestion:
    """A suggested care task and the reason for suggesting it."""

    task: CareTask
    reason: str
    status: str = "pending"

    def accept(self) -> None:
        """Accept the suggested task."""
        pass

    def deny(self) -> None:
        """Deny the suggested task."""
        pass


@dataclass
class DailySchedule:
    """The selected care tasks for a particular day."""

    schedule_date: date
    scheduled_tasks: list[CareTask] = field(default_factory=list)
    total_minutes: int = 0

    def add_task(self, task: CareTask) -> None:
        """Add a care task to this schedule."""
        pass

    def remove_task(self, task: CareTask) -> None:
        """Remove a care task from this schedule."""
        pass

    def explain_plan(self) -> None:
        """Explain why tasks were included in the schedule."""
        pass


@dataclass
class Scheduler:
    """Coordinates owner, pet, and task data to build a daily plan."""

    owner: Owner
    pets: list[Pet] = field(default_factory=list)
    tasks: list[CareTask] = field(default_factory=list)

    def generate_schedule(self) -> None:
        """Create a daily schedule based on available time and priorities."""
        pass

    def rank_tasks(self) -> None:
        """Order tasks according to scheduling priority."""
        pass

    def filter_tasks_by_available_time(self) -> None:
        """Select tasks that fit within the owner's available time."""
        pass
