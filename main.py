"""
PawPal+ Demo Script
Tests the scheduling logic in the terminal before UI integration.
"""

from datetime import date
from src.pawpal_system import (
    Task, Pet, Owner, OwnerPreferences,
    Priority, TaskCategory,
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

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
