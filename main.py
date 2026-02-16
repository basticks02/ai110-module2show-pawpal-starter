"""
PawPal+ Demo Script
Tests the scheduling logic in the terminal before UI integration.
"""

from datetime import date
from src.pawpal_system import (
    Task, Pet, Owner, OwnerPreferences,
    Priority, TaskCategory, TaskFrequency,
    PriorityGreedyScheduler
)


def main():
    print("=" * 60)
    print("🐾 PawPal+ Scheduling Demo")
    print("=" * 60)

    # Create an owner
    owner = Owner(name="Jordan", available_time_minutes=120)
    print(f"\n👤 Owner: {owner.name}")
    print(f"   Available time: {owner.available_time_minutes} minutes")

    # Create pets
    dog = Pet(name="Mochi", species="dog", age_years=3.5)
    cat = Pet(name="Whiskers", species="cat", age_years=2.0)

    # Add tasks to dog
    dog.add_task(Task(
        title="Morning walk",
        duration_minutes=30,
        priority=Priority.HIGH,
        category=TaskCategory.WALK,
        description="Daily exercise walk around the neighborhood"
    ))

    dog.add_task(Task(
        title="Feed breakfast",
        duration_minutes=10,
        priority=Priority.CRITICAL,
        category=TaskCategory.FEEDING,
        description="Kibble with vitamins"
    ))

    dog.add_task(Task(
        title="Playtime",
        duration_minutes=20,
        priority=Priority.MEDIUM,
        category=TaskCategory.ENRICHMENT,
        description="Interactive play with toys"
    ))

    dog.add_task(Task(
        title="Grooming",
        duration_minutes=45,
        priority=Priority.LOW,
        category=TaskCategory.GROOMING,
        description="Brush coat and check for ticks"
    ))

    # Add tasks to cat
    cat.add_task(Task(
        title="Feed breakfast",
        duration_minutes=5,
        priority=Priority.CRITICAL,
        category=TaskCategory.FEEDING,
        description="Wet food"
    ))

    cat.add_task(Task(
        title="Litter box cleaning",
        duration_minutes=10,
        priority=Priority.HIGH,
        category=TaskCategory.GROOMING,
        description="Scoop and refresh litter"
    ))

    cat.add_task(Task(
        title="Play with feather toy",
        duration_minutes=15,
        priority=Priority.MEDIUM,
        category=TaskCategory.ENRICHMENT,
        description="Interactive play session"
    ))

    # Add pets to owner
    owner.add_pet(dog)
    owner.add_pet(cat)

    print(f"\n🐕 Pet: {dog.name} ({dog.species}, {dog.age_years} years)")
    print(f"   Tasks: {len(dog.tasks)}")
    for task in dog.tasks:
        print(f"   - {task.title} ({task.duration_minutes} min, {task.priority.name})")

    print(f"\n🐈 Pet: {cat.name} ({cat.species}, {cat.age_years} years)")
    print(f"   Tasks: {len(cat.tasks)}")
    for task in cat.tasks:
        print(f"   - {task.title} ({task.duration_minutes} min, {task.priority.name})")

    # Calculate total task time
    total_time = owner.calculate_total_task_time()
    print(f"\n📊 Total task time needed: {total_time} minutes")
    print(f"   Available time: {owner.available_time_minutes} minutes")

    if total_time > owner.available_time_minutes:
        print(f"   ⚠️  Not enough time! Need {total_time - owner.available_time_minutes} more minutes")
    else:
        print(f"   ✅ Enough time with {owner.available_time_minutes - total_time} minutes to spare")

    # Generate schedule
    print("\n" + "=" * 60)
    print("📅 Generating Schedule...")
    print("=" * 60)

    scheduler = PriorityGreedyScheduler(owner, date.today())
    schedule = scheduler.generate_schedule()

    # Display schedule
    print(f"\n📋 Today's Schedule ({schedule.date}):")
    print(f"   Scheduled: {len(schedule.scheduled_tasks)} tasks")
    print(f"   Unscheduled: {len(schedule.unscheduled_tasks)} tasks")
    print(f"   Total time: {schedule.total_time_minutes} minutes")
    print(f"   Utilization: {schedule.utilization_percentage}%")

    if schedule.scheduled_tasks:
        print("\n⏰ Scheduled Tasks:")
        for st in schedule.scheduled_tasks:
            end_time = st.get_end_time()
            print(f"\n   [{st.scheduled_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}] {st.task.title}")
            print(f"      Duration: {st.task.duration_minutes} min")
            print(f"      Priority: {st.task.priority.name}")
            print(f"      Category: {st.task.category.value}")
            print(f"      Reasoning: {st.reasoning}")

    if schedule.unscheduled_tasks:
        print("\n❌ Unscheduled Tasks:")
        for task in schedule.unscheduled_tasks:
            print(f"   - {task.title} ({task.duration_minutes} min, {task.priority.name})")

    # Display explanation
    print("\n" + "=" * 60)
    print("📝 Schedule Explanation:")
    print("=" * 60)
    print(schedule.generate_explanation())

    # Validate schedule
    print("\n" + "=" * 60)
    print("✅ Validation:")
    print("=" * 60)
    is_valid = schedule.validate()
    if is_valid:
        print("✅ Schedule is valid (no conflicts detected)")
    else:
        print("❌ Schedule has conflicts!")

    # ============================================================================
    # Demo: Algorithmic Features (Phase 4)
    # ============================================================================

    print("\n" + "=" * 60)
    print("🧮 Algorithmic Features Demo")
    print("=" * 60)

    print("\n--- Sorting Tasks ---")

    # Sort by priority
    print("\n1. Tasks sorted by priority (highest first):")
    sorted_by_priority = owner.get_tasks_sorted_by_priority()
    for task in sorted_by_priority[:5]:  # Show top 5
        print(f"   {task.priority.name:8} - {task.title} ({task.duration_minutes} min)")

    # Sort by time
    print("\n2. Tasks sorted by duration (shortest first):")
    sorted_by_time = owner.get_tasks_sorted_by_time()
    for task in sorted_by_time[:5]:  # Show top 5
        print(f"   {task.duration_minutes:3} min - {task.title} ({task.priority.name})")

    print("\n--- Filtering Tasks ---")

    # Filter incomplete tasks
    all_tasks_check = owner.get_all_tasks()
    incomplete_tasks = owner.get_incomplete_tasks()
    print(f"\n3. Incomplete tasks: {len(incomplete_tasks)} out of {len(all_tasks_check)}")

    # Filter by category
    walk_tasks = []
    for pet in owner.pets:
        walk_tasks.extend(pet.get_tasks_by_category(TaskCategory.WALK))
    print(f"4. Walk tasks across all pets: {len(walk_tasks)}")
    for task in walk_tasks:
        print(f"   - {task.title}")

    print("\n--- Recurring Tasks ---")

    # Add a recurring daily task
    recurring_task = Task(
        title="Evening walk",
        duration_minutes=20,
        priority=Priority.HIGH,
        category=TaskCategory.WALK,
        description="Daily evening exercise",
        frequency=TaskFrequency.DAILY
    )
    dog.add_task(recurring_task)
    print(f"\n5. Added recurring task: {recurring_task.title} ({recurring_task.frequency.value})")

    # Mark complete and generate next occurrence
    print(f"   Before: is_completed = {recurring_task.is_completed}")
    next_task = recurring_task.mark_complete()
    print(f"   After marking complete: is_completed = {recurring_task.is_completed}")
    if next_task:
        print(f"   ✅ Auto-generated next occurrence: {next_task.title}")
        print(f"      Frequency: {next_task.frequency.value}")
        print(f"      Completed: {next_task.is_completed}")

    print("\n--- Conflict Detection ---")

    # Check for conflicts in the schedule
    conflicts = schedule.detect_conflicts()
    if conflicts:
        print(f"\n6. ⚠️  Found {len(conflicts)} conflict(s):")
        for conf in conflicts:
            print(f"   - {conf['task1']} ({conf['task1_time']})")
            print(f"     conflicts with")
            print(f"     {conf['task2']} ({conf['task2_time']})")
    else:
        print("6. ✅ No conflicts detected in the schedule")

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
