"""
PawPal+ System - Backend Logic Layer
This module contains all the core classes for the PawPal+ pet care scheduling system.
"""

from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import date, time
from typing import List, Optional, Dict


# ============================================================================
# Enumerations
# ============================================================================

class Priority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskCategory(Enum):
    """Categories of pet care tasks."""
    WALK = "walk"
    FEEDING = "feeding"
    MEDICATION = "medication"
    GROOMING = "grooming"
    ENRICHMENT = "enrichment"


class TaskFrequency(Enum):
    """Frequency for recurring tasks."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# ============================================================================
# Domain Models
# ============================================================================

@dataclass
class Task:
    """Represents a single pet care activity."""
    title: str
    duration_minutes: int
    priority: Priority
    category: TaskCategory
    description: str = ""
    frequency: 'TaskFrequency' = None
    is_completed: bool = False

    def __post_init__(self):
        """Initialize frequency to ONCE if not specified."""
        if self.frequency is None:
            from sys import modules
            # Import TaskFrequency if not already available
            if 'TaskFrequency' not in dir(modules[__name__]):
                self.frequency = TaskFrequency.ONCE
            else:
                self.frequency = TaskFrequency.ONCE

    def get_priority_score(self) -> int:
        """Returns numeric priority score for comparison."""
        return self.priority.value

    def mark_complete(self) -> Optional['Task']:
        """
        Marks this task as complete.
        For recurring tasks, returns a new task for the next occurrence.
        For one-time tasks, just marks complete and returns None.
        """
        self.is_completed = True

        # If it's a recurring task, create next occurrence
        if self.frequency != TaskFrequency.ONCE:
            return Task(
                title=self.title,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                category=self.category,
                description=self.description,
                frequency=self.frequency,
                is_completed=False
            )
        return None


@dataclass
class Pet:
    """Represents a pet with associated care tasks."""
    name: str
    species: str
    age_years: float = 0.0
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Adds a task to this pet's care routine."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Removes a task from this pet's care routine."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """Returns all tasks matching the given priority."""
        return [task for task in self.tasks if task.priority == priority]

    def get_tasks_by_category(self, category: TaskCategory) -> List[Task]:
        """Returns all tasks matching the given category."""
        return [task for task in self.tasks if task.category == category]

    def get_tasks_by_completion(self, completed: bool = False) -> List[Task]:
        """Returns tasks filtered by completion status."""
        return [task for task in self.tasks if task.is_completed == completed]

    def get_incomplete_tasks(self) -> List[Task]:
        """Returns all incomplete tasks."""
        return self.get_tasks_by_completion(completed=False)

    def sort_tasks_by_time(self, reverse: bool = False) -> List[Task]:
        """Returns tasks sorted by duration."""
        return sorted(self.tasks, key=lambda t: t.duration_minutes, reverse=reverse)

    def sort_tasks_by_priority(self, reverse: bool = True) -> List[Task]:
        """Returns tasks sorted by priority (highest first by default)."""
        return sorted(self.tasks, key=lambda t: t.get_priority_score(), reverse=reverse)


@dataclass
class OwnerPreferences:
    """Encapsulates owner's scheduling preferences."""
    preferred_task_order: List[TaskCategory] = field(default_factory=list)
    priority_threshold: Priority = Priority.LOW
    group_similar_tasks: bool = False

    def should_group_tasks(self, task1: Task, task2: Task) -> bool:
        """Determines if two tasks should be grouped together."""
        if not self.group_similar_tasks:
            return False
        return task1.category == task2.category


@dataclass
class Owner:
    """Represents the pet owner with constraints and preferences."""
    name: str
    available_time_minutes: int
    pets: List[Pet] = field(default_factory=list)
    preferences: Optional[OwnerPreferences] = None

    def __post_init__(self):
        """Initialize preferences if not provided."""
        if self.preferences is None:
            self.preferences = OwnerPreferences()

    def add_pet(self, pet: Pet) -> None:
        """Adds a pet to the owner's care."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Removes a pet from the owner's care."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_all_tasks(self) -> List[Task]:
        """Returns all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def calculate_total_task_time(self) -> int:
        """Calculates total time needed for all tasks."""
        return sum(task.duration_minutes for task in self.get_all_tasks())

    def get_incomplete_tasks(self) -> List[Task]:
        """Returns all incomplete tasks across all pets."""
        return [task for task in self.get_all_tasks() if not task.is_completed]

    def get_tasks_sorted_by_priority(self) -> List[Task]:
        """Returns all tasks sorted by priority (highest first)."""
        return sorted(self.get_all_tasks(), key=lambda t: t.get_priority_score(), reverse=True)

    def get_tasks_sorted_by_time(self) -> List[Task]:
        """Returns all tasks sorted by duration (shortest first)."""
        return sorted(self.get_all_tasks(), key=lambda t: t.duration_minutes)


# ============================================================================
# Scheduling Models
# ============================================================================

@dataclass
class ScheduledTask:
    """A task with assigned scheduling information."""
    task: Task
    scheduled_time: time
    order_index: int
    reasoning: str = ""

    def get_end_time(self) -> time:
        """Calculates when this task will end."""
        from datetime import datetime, timedelta
        # Convert time to datetime, add duration, convert back to time
        dt = datetime.combine(datetime.today(), self.scheduled_time)
        end_dt = dt + timedelta(minutes=self.task.duration_minutes)
        return end_dt.time()

    def conflicts_with(self, other: 'ScheduledTask') -> bool:
        """Checks if this task conflicts with another scheduled task."""
        # Simple overlap check: if one task starts before the other ends
        return not (self.get_end_time() <= other.scheduled_time or
                   other.get_end_time() <= self.scheduled_time)


@dataclass
class Schedule:
    """Represents a complete daily schedule with explanations."""
    date: date
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    unscheduled_tasks: List[Task] = field(default_factory=list)
    total_time_minutes: int = 0
    utilization_percentage: float = 0.0

    def calculate_total_time(self) -> int:
        """Calculates total time of all scheduled tasks."""
        total = sum(st.task.duration_minutes for st in self.scheduled_tasks)
        self.total_time_minutes = total
        return total

    def calculate_utilization(self, available_time: int) -> float:
        """Calculates percentage of available time used."""
        if available_time == 0:
            self.utilization_percentage = 0.0
            return 0.0
        utilization = (self.total_time_minutes / available_time) * 100
        self.utilization_percentage = round(utilization, 2)
        return self.utilization_percentage

    def validate(self) -> bool:
        """Validates the schedule for conflicts and constraint violations."""
        # Check for time conflicts between scheduled tasks
        for i, task1 in enumerate(self.scheduled_tasks):
            for task2 in self.scheduled_tasks[i+1:]:
                if task1.conflicts_with(task2):
                    return False
        return True

    def detect_conflicts(self) -> List[Dict]:
        """
        Detects and returns detailed information about any time conflicts.
        Returns list of conflict dictionaries with task details.
        """
        conflicts = []
        for i, task1 in enumerate(self.scheduled_tasks):
            for j, task2 in enumerate(self.scheduled_tasks[i+1:], start=i+1):
                if task1.conflicts_with(task2):
                    conflicts.append({
                        'task1': task1.task.title,
                        'task1_time': f"{task1.scheduled_time.strftime('%H:%M')} - {task1.get_end_time().strftime('%H:%M')}",
                        'task2': task2.task.title,
                        'task2_time': f"{task2.scheduled_time.strftime('%H:%M')} - {task2.get_end_time().strftime('%H:%M')}",
                        'overlap': 'These tasks have overlapping time slots'
                    })
        return conflicts

    def generate_explanation(self) -> str:
        """Generates human-readable explanation of scheduling decisions."""
        if not self.scheduled_tasks and not self.unscheduled_tasks:
            return "No tasks to schedule."

        explanation = []
        explanation.append(f"Scheduled {len(self.scheduled_tasks)} task(s) for {self.date}.")
        explanation.append(f"Total time: {self.total_time_minutes} minutes ({self.utilization_percentage}% utilization).")

        if self.unscheduled_tasks:
            explanation.append(f"\n{len(self.unscheduled_tasks)} task(s) could not be scheduled:")
            for task in self.unscheduled_tasks:
                explanation.append(f"  - {task.title} ({task.duration_minutes} min, {task.priority.name})")

        return "\n".join(explanation)

    def to_dict(self) -> Dict:
        """Converts schedule to dictionary for UI display."""
        return {
            "date": str(self.date),
            "scheduled_tasks": [
                {
                    "title": st.task.title,
                    "time": str(st.scheduled_time),
                    "duration": st.task.duration_minutes,
                    "priority": st.task.priority.name,
                    "category": st.task.category.value,
                    "reasoning": st.reasoning
                }
                for st in self.scheduled_tasks
            ],
            "unscheduled_tasks": [
                {
                    "title": task.title,
                    "duration": task.duration_minutes,
                    "priority": task.priority.name,
                    "category": task.category.value
                }
                for task in self.unscheduled_tasks
            ],
            "total_time_minutes": self.total_time_minutes,
            "utilization_percentage": self.utilization_percentage
        }


# ============================================================================
# Scheduling Algorithms
# ============================================================================

class Scheduler(ABC):
    """Abstract base class for scheduling algorithms."""

    def __init__(self, owner: Owner, schedule_date: date):
        self.owner = owner
        self.date = schedule_date

    @abstractmethod
    def generate_schedule(self) -> Schedule:
        """Generates a schedule based on owner's pets and constraints."""
        pass

    def _validate_constraints(self, schedule: Schedule) -> bool:
        """Validates schedule against constraints."""
        return schedule.validate()

    def _calculate_task_score(self, task: Task, current_time: time) -> float:
        """Calculates a score for task prioritization."""
        # Base implementation: just return priority score
        return float(task.get_priority_score())


class PriorityGreedyScheduler(Scheduler):
    """Concrete scheduler using priority-based greedy algorithm."""

    def __init__(self, owner: Owner, schedule_date: date, priority_weights: Optional[Dict] = None):
        super().__init__(owner, schedule_date)
        self.priority_weights = priority_weights or {
            Priority.CRITICAL: 4.0,
            Priority.HIGH: 3.0,
            Priority.MEDIUM: 2.0,
            Priority.LOW: 1.0
        }

    def generate_schedule(self) -> Schedule:
        """
        Generates schedule using priority-based greedy algorithm.
        Higher priority tasks are scheduled first.
        """
        from datetime import datetime, timedelta

        # Get all tasks and sort by priority (highest first)
        all_tasks = self.owner.get_all_tasks()
        available_tasks = sorted(all_tasks, key=lambda t: t.get_priority_score(), reverse=True)

        # Initialize schedule
        schedule = Schedule(date=self.date)

        # Handle edge case: no tasks
        if not available_tasks:
            return schedule

        # Handle edge case: no time available
        if self.owner.available_time_minutes <= 0:
            schedule.unscheduled_tasks = available_tasks.copy()
            schedule.calculate_total_time()
            schedule.calculate_utilization(self.owner.available_time_minutes)
            return schedule

        # Start scheduling from 6:00 AM
        current_time = time(6, 0)
        remaining_time = self.owner.available_time_minutes
        order_index = 0

        # Greedy algorithm: schedule highest priority tasks that fit
        while remaining_time > 0 and available_tasks:
            # Find the next task that fits
            next_task = self._select_next_task(available_tasks, current_time)

            if next_task is None:
                # No more tasks can fit
                break

            # Check if task fits in remaining time
            if not self._can_fit_task(next_task, current_time, remaining_time):
                # Task doesn't fit, remove from available and try next
                available_tasks.remove(next_task)
                schedule.unscheduled_tasks.append(next_task)
                continue

            # Schedule the task
            score = self._calculate_task_score(next_task, current_time)
            reasoning = self._generate_reasoning(next_task, score, available_tasks[:3])

            scheduled_task = ScheduledTask(
                task=next_task,
                scheduled_time=current_time,
                order_index=order_index,
                reasoning=reasoning
            )

            schedule.scheduled_tasks.append(scheduled_task)

            # Update state
            available_tasks.remove(next_task)
            remaining_time -= next_task.duration_minutes
            order_index += 1

            # Move current time forward
            dt = datetime.combine(datetime.today(), current_time)
            dt += timedelta(minutes=next_task.duration_minutes)
            current_time = dt.time()

        # Any remaining tasks are unscheduled
        schedule.unscheduled_tasks.extend(available_tasks)

        # Finalize schedule
        schedule.calculate_total_time()
        schedule.calculate_utilization(self.owner.available_time_minutes)

        return schedule

    def _select_next_task(self, available_tasks: List[Task], current_time: time) -> Optional[Task]:
        """Selects the next task to schedule based on priority and scoring."""
        if not available_tasks:
            return None

        # Find highest scoring task
        best_task = None
        best_score = -1

        for task in available_tasks:
            score = self._calculate_task_score(task, current_time)
            if score > best_score:
                best_score = score
                best_task = task

        return best_task

    def _can_fit_task(self, task: Task, current_time: time, remaining_time: int) -> bool:
        """Checks if a task can fit in remaining time."""
        return task.duration_minutes <= remaining_time

    def _generate_reasoning(self, task: Task, score: float, alternatives: List[Task]) -> str:
        """Generates explanation for why this task was chosen."""
        reasons = []

        # Priority-based reasoning
        if task.priority == Priority.CRITICAL:
            reasons.append("CRITICAL priority - must be completed")
        elif task.priority == Priority.HIGH:
            reasons.append("HIGH priority task")
        elif task.priority == Priority.MEDIUM:
            reasons.append("MEDIUM priority task")
        else:
            reasons.append("LOW priority task")

        # Category-based reasoning
        if task.category == TaskCategory.MEDICATION:
            reasons.append("medication should not be delayed")
        elif task.category == TaskCategory.FEEDING:
            reasons.append("feeding is essential care")
        elif task.category == TaskCategory.WALK:
            reasons.append("exercise is important for pet health")

        # Mention alternatives if any
        if len(alternatives) > 1:
            other_priorities = [t.priority.name for t in alternatives[1:3]]
            if other_priorities:
                reasons.append(f"chosen over {', '.join(other_priorities)} priority tasks")

        return ". ".join(reasons) + "."
