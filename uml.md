# PawPal+ UML Class Diagram

## Mermaid Class Diagram

```mermaid
classDiagram
    %% Enumerations
    class Priority {
        <<enumeration>>
        LOW
        MEDIUM
        HIGH
        CRITICAL
    }

    class TaskCategory {
        <<enumeration>>
        WALK
        FEEDING
        MEDICATION
        GROOMING
        ENRICHMENT
    }

    %% Core Classes
    class Task {
        +title: str
        +duration_minutes: int
        +priority: Priority
        +category: TaskCategory
        +description: str
        +get_priority_score() int
    }

    class Pet {
        +name: str
        +species: str
        +age_years: float
        +tasks: list~Task~
        +add_task(task)
        +get_tasks_by_priority(priority) list~Task~
        +get_tasks_by_category(category) list~Task~
    }

    class Owner {
        +name: str
        +available_time_minutes: int
        +pets: list~Pet~
        +preferences: OwnerPreferences
        +add_pet(pet)
        +get_all_tasks() list~Task~
        +calculate_total_task_time() int
    }

    class OwnerPreferences {
        +preferred_task_order: list~TaskCategory~
        +priority_threshold: Priority
        +group_similar_tasks: bool
        +should_group_tasks(task1, task2) bool
    }

    class Schedule {
        +date: date
        +scheduled_tasks: list~ScheduledTask~
        +unscheduled_tasks: list~Task~
        +total_time_minutes: int
        +utilization_percentage: float
        +calculate_utilization(available_time) float
        +generate_explanation() str
    }

    class ScheduledTask {
        +task: Task
        +scheduled_time: time
        +order_index: int
        +reasoning: str
        +get_end_time() time
    }

    class Scheduler {
        <<abstract>>
        +owner: Owner
        +date: date
        +generate_schedule() Schedule
    }

    class PriorityGreedyScheduler {
        +priority_weights: dict
        +generate_schedule() Schedule
    }

    %% Relationships
    Owner "1" -- "*" Pet : manages
    Owner "1" -- "1" OwnerPreferences : has
    Pet "1" *-- "*" Task : owns
    Task -- Priority
    Task -- TaskCategory

    Scheduler -- Owner : uses
    Scheduler ..> Schedule : creates
    PriorityGreedyScheduler --|> Scheduler : inherits

    Schedule "1" *-- "*" ScheduledTask : contains
    ScheduledTask --> Task : references
```

## Class Responsibilities

**Task**: Represents a single pet care activity with duration, priority, and category

**Pet**: Manages a pet with their associated care tasks

**Owner**: Represents the pet owner with time budget, pets, and scheduling preferences

**OwnerPreferences**: Encapsulates owner's preferences for task scheduling

**Scheduler**: Abstract base class defining the scheduling algorithm interface

**PriorityGreedyScheduler**: Concrete scheduler that prioritizes tasks by priority level

**Schedule**: Output object containing scheduled tasks, unscheduled tasks, and explanations

**ScheduledTask**: A task with assigned time slot, order, and reasoning
