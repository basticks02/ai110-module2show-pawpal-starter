"""
PawPal+ Test Suite
Tests for core scheduling functionality.
"""

import pytest
from datetime import date, time
from src.pawpal_system import (
    Task, Pet, Owner, OwnerPreferences,
    Priority, TaskCategory,
    PriorityGreedyScheduler,
    Schedule, ScheduledTask
)


# ============================================================================
# Task Tests
# ============================================================================

def test_task_creation():
    """Test that a task can be created with required attributes."""
    task = Task(
        title="Morning walk",
        duration_minutes=30,
        priority=Priority.HIGH,
        category=TaskCategory.WALK
    )
    assert task.title == "Morning walk"
    assert task.duration_minutes == 30
    assert task.priority == Priority.HIGH
    assert task.category == TaskCategory.WALK


def test_task_priority_score():
    """Test that get_priority_score returns correct numeric value."""
    critical_task = Task("Emergency", 10, Priority.CRITICAL, TaskCategory.MEDICATION)
    high_task = Task("Important", 10, Priority.HIGH, TaskCategory.WALK)
    medium_task = Task("Normal", 10, Priority.MEDIUM, TaskCategory.FEEDING)
    low_task = Task("Optional", 10, Priority.LOW, TaskCategory.ENRICHMENT)

    assert critical_task.get_priority_score() == 4
    assert high_task.get_priority_score() == 3
    assert medium_task.get_priority_score() == 2
    assert low_task.get_priority_score() == 1


# ============================================================================
# Pet Tests
# ============================================================================

def test_pet_creation():
    """Test that a pet can be created."""
    pet = Pet(name="Buddy", species="dog", age_years=5.0)
    assert pet.name == "Buddy"
    assert pet.species == "dog"
    assert pet.age_years == 5.0
    assert len(pet.tasks) == 0


def test_pet_add_task():
    """Test that adding a task to a pet increases task count."""
    pet = Pet(name="Mochi", species="dog")
    task = Task("Walk", 30, Priority.HIGH, TaskCategory.WALK)

    initial_count = len(pet.tasks)
    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1
    assert task in pet.tasks


def test_pet_remove_task():
    """Test that removing a task from a pet decreases task count."""
    pet = Pet(name="Whiskers", species="cat")
    task = Task("Feed", 5, Priority.CRITICAL, TaskCategory.FEEDING)

    pet.add_task(task)
    assert task in pet.tasks

    pet.remove_task(task)
    assert task not in pet.tasks


def test_pet_get_tasks_by_priority():
    """Test filtering tasks by priority."""
    pet = Pet(name="Rex", species="dog")
    high_task = Task("Walk", 30, Priority.HIGH, TaskCategory.WALK)
    low_task = Task("Groom", 20, Priority.LOW, TaskCategory.GROOMING)

    pet.add_task(high_task)
    pet.add_task(low_task)

    high_priority_tasks = pet.get_tasks_by_priority(Priority.HIGH)
    assert len(high_priority_tasks) == 1
    assert high_task in high_priority_tasks


def test_pet_get_tasks_by_category():
    """Test filtering tasks by category."""
    pet = Pet(name="Fluffy", species="cat")
    walk = Task("Walk", 15, Priority.MEDIUM, TaskCategory.WALK)
    feed = Task("Feed", 5, Priority.CRITICAL, TaskCategory.FEEDING)

    pet.add_task(walk)
    pet.add_task(feed)

    feeding_tasks = pet.get_tasks_by_category(TaskCategory.FEEDING)
    assert len(feeding_tasks) == 1
    assert feed in feeding_tasks


# ============================================================================
# Owner Tests
# ============================================================================

def test_owner_creation():
    """Test that an owner can be created with time budget."""
    owner = Owner(name="Alex", available_time_minutes=120)
    assert owner.name == "Alex"
    assert owner.available_time_minutes == 120
    assert len(owner.pets) == 0


def test_owner_add_pet():
    """Test that adding a pet to owner works."""
    owner = Owner(name="Jordan", available_time_minutes=180)
    pet = Pet(name="Buddy", species="dog")

    owner.add_pet(pet)
    assert len(owner.pets) == 1
    assert pet in owner.pets


def test_owner_get_all_tasks():
    """Test that owner can aggregate tasks from all pets."""
    owner = Owner(name="Sam", available_time_minutes=120)

    dog = Pet(name="Rex", species="dog")
    dog.add_task(Task("Walk", 30, Priority.HIGH, TaskCategory.WALK))
    dog.add_task(Task("Feed", 10, Priority.CRITICAL, TaskCategory.FEEDING))

    cat = Pet(name="Whiskers", species="cat")
    cat.add_task(Task("Feed", 5, Priority.CRITICAL, TaskCategory.FEEDING))

    owner.add_pet(dog)
    owner.add_pet(cat)

    all_tasks = owner.get_all_tasks()
    assert len(all_tasks) == 3


def test_owner_calculate_total_task_time():
    """Test that total task time is calculated correctly."""
    owner = Owner(name="Taylor", available_time_minutes=100)
    pet = Pet(name="Max", species="dog")

    pet.add_task(Task("Walk", 30, Priority.HIGH, TaskCategory.WALK))
    pet.add_task(Task("Feed", 10, Priority.CRITICAL, TaskCategory.FEEDING))
    pet.add_task(Task("Play", 20, Priority.MEDIUM, TaskCategory.ENRICHMENT))

    owner.add_pet(pet)

    total_time = owner.calculate_total_task_time()
    assert total_time == 60  # 30 + 10 + 20


# ============================================================================
# Scheduler Tests
# ============================================================================

def test_scheduler_empty_tasks():
    """Test that scheduler handles empty task list gracefully."""
    owner = Owner(name="Empty", available_time_minutes=120)
    pet = Pet(name="Lonely", species="dog")
    owner.add_pet(pet)

    scheduler = PriorityGreedyScheduler(owner, date.today())
    schedule = scheduler.generate_schedule()

    assert len(schedule.scheduled_tasks) == 0
    assert len(schedule.unscheduled_tasks) == 0
    assert schedule.total_time_minutes == 0


def test_scheduler_no_time_available():
    """Test that scheduler handles zero available time."""
    owner = Owner(name="Busy", available_time_minutes=0)
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(Task("Walk", 30, Priority.HIGH, TaskCategory.WALK))
    owner.add_pet(pet)

    scheduler = PriorityGreedyScheduler(owner, date.today())
    schedule = scheduler.generate_schedule()

    assert len(schedule.scheduled_tasks) == 0
    assert len(schedule.unscheduled_tasks) == 1
    assert schedule.utilization_percentage == 0.0


def test_scheduler_priority_ordering():
    """Test that higher priority tasks are scheduled first."""
    owner = Owner(name="Jordan", available_time_minutes=100)
    pet = Pet(name="Mochi", species="dog")

    low_task = Task("Groom", 20, Priority.LOW, TaskCategory.GROOMING)
    high_task = Task("Walk", 30, Priority.HIGH, TaskCategory.WALK)
    critical_task = Task("Medication", 10, Priority.CRITICAL, TaskCategory.MEDICATION)

    pet.add_task(low_task)
    pet.add_task(high_task)
    pet.add_task(critical_task)
    owner.add_pet(pet)

    scheduler = PriorityGreedyScheduler(owner, date.today())
    schedule = scheduler.generate_schedule()

    # All tasks should fit, and CRITICAL should be first
    assert len(schedule.scheduled_tasks) == 3
    assert schedule.scheduled_tasks[0].task == critical_task
    assert schedule.scheduled_tasks[1].task == high_task
    assert schedule.scheduled_tasks[2].task == low_task


def test_scheduler_insufficient_time():
    """Test that scheduler handles insufficient time correctly."""
    owner = Owner(name="Alex", available_time_minutes=40)
    pet = Pet(name="Rex", species="dog")

    pet.add_task(Task("Feed", 10, Priority.CRITICAL, TaskCategory.FEEDING))
    pet.add_task(Task("Walk", 30, Priority.HIGH, TaskCategory.WALK))
    pet.add_task(Task("Groom", 45, Priority.LOW, TaskCategory.GROOMING))

    owner.add_pet(pet)

    scheduler = PriorityGreedyScheduler(owner, date.today())
    schedule = scheduler.generate_schedule()

    # Feed (10) + Walk (30) = 40 minutes, Groom won't fit
    assert len(schedule.scheduled_tasks) == 2
    assert len(schedule.unscheduled_tasks) == 1
    assert schedule.total_time_minutes == 40


def test_schedule_validation():
    """Test that schedule validation detects valid schedules."""
    owner = Owner(name="Test", available_time_minutes=60)
    pet = Pet(name="Pet", species="dog")
    pet.add_task(Task("Task1", 20, Priority.HIGH, TaskCategory.WALK))
    owner.add_pet(pet)

    scheduler = PriorityGreedyScheduler(owner, date.today())
    schedule = scheduler.generate_schedule()

    # Schedule should be valid (no overlapping tasks)
    assert schedule.validate() is True


def test_schedule_utilization_calculation():
    """Test that utilization percentage is calculated correctly."""
    owner = Owner(name="Test", available_time_minutes=100)
    pet = Pet(name="Pet", species="dog")
    pet.add_task(Task("Task", 50, Priority.HIGH, TaskCategory.WALK))
    owner.add_pet(pet)

    scheduler = PriorityGreedyScheduler(owner, date.today())
    schedule = scheduler.generate_schedule()

    # 50 minutes of 100 available = 50% utilization
    assert schedule.utilization_percentage == 50.0


# ============================================================================
# Integration Tests
# ============================================================================

def test_end_to_end_scheduling():
    """Test complete scheduling workflow."""
    # Create owner
    owner = Owner(name="Jordan", available_time_minutes=90)

    # Create pet with multiple tasks
    dog = Pet(name="Mochi", species="dog", age_years=3.5)
    dog.add_task(Task("Feed", 10, Priority.CRITICAL, TaskCategory.FEEDING))
    dog.add_task(Task("Walk", 30, Priority.HIGH, TaskCategory.WALK))
    dog.add_task(Task("Play", 20, Priority.MEDIUM, TaskCategory.ENRICHMENT))
    dog.add_task(Task("Groom", 45, Priority.LOW, TaskCategory.GROOMING))

    owner.add_pet(dog)

    # Generate schedule
    scheduler = PriorityGreedyScheduler(owner, date.today())
    schedule = scheduler.generate_schedule()

    # Verify results
    assert len(schedule.scheduled_tasks) > 0
    assert schedule.validate() is True
    assert schedule.total_time_minutes <= owner.available_time_minutes

    # Verify priority ordering in schedule
    priorities = [st.task.priority for st in schedule.scheduled_tasks]
    sorted_priorities = sorted(priorities, key=lambda p: p.value, reverse=True)
    assert priorities == sorted_priorities
