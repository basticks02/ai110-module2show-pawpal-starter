# PawPal+ Project Reflection

## 1. System Design

### Core User Actions

Based on the PawPal+ requirements, users should be able to perform these three core actions:

1. **Add and manage pets with their care tasks** - Users should input pet information (name, species, age) and define care tasks for each pet, including task details like duration, priority, and category (walk, feeding, medication, etc.).

2. **Generate a daily care schedule** - Users should specify their available time and preferences, then generate an optimized daily schedule that prioritizes and orders tasks based on constraints like time budget, task priority, and owner preferences.

3. **View and understand the schedule** - Users should see a clear, time-ordered schedule showing which tasks were selected, when they should be done, and explanations for why certain tasks were prioritized or left unscheduled.

**a. Initial design**

My initial UML design follows an object-oriented architecture with clear separation between domain models and scheduling logic:

**Core Domain Classes:**
- **Task**: Represents a single pet care activity with attributes like title, duration, priority (LOW/MEDIUM/HIGH/CRITICAL), and category (WALK, FEEDING, MEDICATION, GROOMING, ENRICHMENT). Responsible for storing task details and calculating priority scores.

- **Pet**: Represents a pet with associated care tasks. Manages the collection of tasks and provides methods to filter tasks by priority or category.

- **Owner**: Represents the pet owner who manages multiple pets and has time constraints. Aggregates all pets, tracks available time budget, and stores scheduling preferences. Responsible for providing access to all tasks across all pets.

- **OwnerPreferences**: Encapsulates the owner's scheduling preferences including preferred task order, priority threshold, and whether to group similar tasks together.

**Scheduling Classes:**
- **Scheduler (Abstract Base)**: Defines the interface for scheduling algorithms. Allows different scheduling strategies to be implemented and swapped easily.

- **PriorityGreedyScheduler**: Concrete implementation that uses a priority-based greedy algorithm. Selects highest priority tasks first that fit within time constraints.

- **Schedule**: Output object containing the generated schedule with scheduled tasks (with time slots and reasoning), unscheduled tasks, utilization metrics, and explanations.

- **ScheduledTask**: Decorator for Task that adds scheduling metadata (scheduled time, order index, reasoning for selection).

**Design Rationale:** This design separates concerns (domain vs scheduling), enables extensibility (multiple scheduler types via inheritance), and emphasizes transparency (detailed explanations for scheduling decisions).

**b. Design changes**

During implementation, I made one significant design change: **adding completion tracking and recurring task support** (Phase 4).

Initially, the design focused solely on generating a single day's schedule. However, I realized that real pet care involves recurring daily tasks (like daily walks and feeding) that shouldn't require manual recreation each day. This led to adding:

1. `is_completed` field to Task - Tracks which tasks are done
2. `frequency` field (TaskFrequency enum) - Defines recurrence pattern
3. `mark_complete()` method - Automatically generates next occurrence for recurring tasks

**Why this change was valuable:**
- Reduces manual work for pet owners who do the same tasks daily
- Makes the system more practical for real-world use
- Follows the DRY principle (Don't Repeat Yourself)
- Adds minimal complexity while providing significant user value

This change demonstrates how implementation insights can improve upon the initial design.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers three primary constraints:

1. **Time Budget** (hard constraint) - Owner's available time is strictly enforced. Tasks that don't fit are marked unscheduled rather than causing schedule overflow.

2. **Task Priority** (primary sorting criterion) - Tasks are sorted CRITICAL → HIGH → MEDIUM → LOW before scheduling. This ensures the most important tasks are always scheduled first when time is limited.

3. **Task Category** (soft constraint used in explanations) - Categories like MEDICATION and FEEDING get emphasized in reasoning to help users understand why certain tasks were prioritized.

**Why these constraints mattered most:**
- **Time is non-negotiable** - You can't create more hours in a day
- **Priority reflects urgency** - Medications can't be skipped, while grooming can wait
- **Category provides context** - Helps users trust the scheduling decisions

I deliberately kept the constraint system simple and transparent rather than adding complex preference weighting that would be harder to explain and debug.

**b. Tradeoffs**

**Tradeoff: Greedy algorithm vs. optimal scheduling**

My scheduler uses a **greedy approach** (schedule highest priority task that fits, then move to next) rather than an optimal algorithm that explores all possible combinations.

**Why this tradeoff is reasonable:**
1. **Performance** - Greedy is O(n²) vs. optimal's O(n! or 2ⁿ), crucial for real-time UI
2. **Explainability** - Each decision has a clear "why" (highest priority available)
3. **Good enough** - For pet care, scheduling high-priority tasks first is usually sufficient
4. **Edge cases are rare** - Cases where greedy fails (e.g., three 40-min tasks vs. four 30-min tasks with 120-min budget) are uncommon in daily pet care

The greedy approach sacrifices theoretical optimality for practical usability - users get instant, understandable schedules rather than waiting for a mathematically perfect but opaque solution.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI (Claude Code) throughout all phases of the project:

**Design Phase (Phase 1):**
- Brainstorming class responsibilities and relationships
- Creating UML diagram with proper inheritance and composition relationships
- Identifying edge cases to handle (empty lists, zero time, conflicts)

**Implementation (Phases 2-4):**
- Generating class skeletons from UML design
- Implementing scheduling algorithm with detailed explanations
- Adding algorithmic features (sorting, filtering, recurring tasks)
- Writing comprehensive test cases

**UI Integration (Phase 3):**
- Building Streamlit forms with session state management
- Creating responsive layout with color coding
- Implementing schedule display with time slots and reasoning

**Most helpful prompts:**
- "Implement a priority-based greedy scheduler that explains each decision"
- "Add tests for edge cases like zero time and insufficient time"
- "Create a Streamlit UI that persists data across interactions"
- Breaking complex tasks into phases helped AI provide focused, quality output

**b. Judgment and verification**

**Moment of careful evaluation: Task.__post_init__() for frequency initialization**

AI initially suggested a complex check for TaskFrequency availability that tried to import and check module state. The code worked but felt overly defensive:

```python
def __post_init__(self):
    if self.frequency is None:
        from sys import modules
        if 'TaskFrequency' not in dir(modules[__name__]):
            self.frequency = TaskFrequency.ONCE
        else:
            self.frequency = TaskFrequency.ONCE
```

**My evaluation:**
- Both branches do the same thing (set to ONCE)
- TaskFrequency is always available (defined in same file)
- The module check adds complexity without value

**Better solution:**
```python
def __post_init__(self):
    if self.frequency is None:
        self.frequency = TaskFrequency.ONCE
```

**Verification method:**
- Tested both versions with `python main.py`
- Confirmed simpler version works identically
- Checked that TaskFrequency enum is always in scope

This taught me that AI sometimes over-engineers defensive code. As the architect, I need to simplify when the extra safety provides no real benefit.

---

## 4. Testing and Verification

**a. What you tested**

I implemented 29+ comprehensive tests organized into three categories:

**Unit Tests (Core Functionality):**
- Task creation, priority scoring, and completion tracking
- Pet task management (add, remove, filter by priority/category)
- Owner multi-pet aggregation and time calculations
- Schedule validation, utilization metrics, and explanation generation
- Scheduler priority ordering and time constraint handling

**Algorithmic Tests (Phase 4 Features):**
- Recurring task generation (daily tasks auto-create next occurrence)
- Completion status filtering (incomplete vs completed)
- Sorting by priority and duration
- Multi-pet task aggregation across owners
- Detailed conflict detection with time slot information

**Edge Case Tests:**
- Empty task lists → valid empty schedule
- Zero available time → all tasks unscheduled with clear explanation
- Insufficient time → highest priority scheduled, rest unscheduled
- All same priority → tiebreaking by category, duration, alphabetical
- Overlapping time slots → conflict detection with detailed warnings

**Why these tests were important:**
- **Core functionality** ensures basic operations work correctly
- **Edge cases** prevent crashes and ensure graceful degradation
- **Algorithm tests** verify intelligent features work as designed
- **Integration tests** confirm components work together correctly

All tests pass successfully, verified through both `main.py` demo and direct testing.

**b. Confidence**

**Confidence Level: ⭐⭐⭐⭐⭐ (5/5)**

I'm highly confident the scheduler works correctly because:

1. **Comprehensive test coverage** - 29+ tests covering happy paths, edge cases, and error conditions
2. **Deterministic algorithm** - Greedy approach produces predictable, repeatable results
3. **Manual verification** - Ran `main.py` demo showing realistic scenarios with 2 pets and 7 tasks
4. **UI validation** - Full Streamlit integration tested with various data inputs
5. **Edge case handling** - System gracefully handles empty lists, zero time, and conflicts

**Edge cases I'd test next with more time:**

1. **Very long task lists** - Stress test with 100+ tasks to verify performance
2. **Pathological priorities** - All CRITICAL or all LOW to test tiebreaking edge cases
3. **Time precision** - Tasks ending exactly at midnight or spanning across days
4. **Concurrent scheduling** - Multiple users/pets with shared resources
5. **Invalid data** - Negative durations, null values, malformed tasks
6. **Recurring task chains** - Daily task marked complete 7 times in a row
7. **Schedule regeneration** - Verify idempotency (same inputs → same output)

These additional tests would push from 95% confidence to 99%, but for a pet care app, the current coverage is production-ready.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the **explanation system** - every scheduled task includes detailed reasoning for why it was chosen.

Example output:
> "CRITICAL priority - must be completed. feeding is essential care. chosen over HIGH, HIGH priority tasks."

**Why this was successful:**
- Makes the "black box" algorithm transparent and trustworthy
- Helps users understand trade-offs when tasks are unscheduled
- Required thoughtful design (storing alternatives during selection)
- Demonstrates that good software isn't just functional - it's understandable

The explanation feature turned a simple greedy algorithm into an educational tool that teaches users about priority-based scheduling while solving their problem.

**b. What you would improve**

**If I had another iteration, I would add:**

1. **Time window constraints** - Let users specify preferred times (e.g., "walks should be morning or evening")
   - Adds complexity but makes schedules more realistic
   - Already designed in initial UML but deferred for MVP

2. **Schedule optimization** - Allow users to tweak generated schedules
   - Drag-and-drop time slot adjustments
   - Manual override for specific tasks
   - Regenerate button to revert to algorithm's suggestion

3. **Historical tracking** - Store completed schedules to show patterns
   - "You walk your dog most days at 7 AM"
   - Suggest optimal times based on history
   - Track completion rates by task type

4. **Multi-day planning** - Generate weekly schedules instead of just daily
   - Distribute grooming across the week
   - Balance high-effort tasks
   - Account for rest days

**c. Key takeaway**

**Key Learning: Incremental complexity through phases is more effective than upfront perfection.**

I initially wanted to implement every feature (time windows, preferences, multi-day scheduling) in the first iteration. Breaking the project into phases (Phase 1: Design, Phase 2: Core, Phase 3: UI, Phase 4: Algorithms) taught me:

- **Each phase delivers value** - After Phase 2, the system worked. Everything else was enhancement.
- **Testing gets easier** - Testing simple features first makes complex features easier to debug
- **Design emerges** - The recurring task feature (Phase 4) wasn't in the original plan but emerged naturally from using the system
- **AI works better with focus** - Asking AI to "implement a scheduler" is vague. Asking it to "implement Phase 2: priority-based greedy scheduling with explanations" gets better results.

This approach mirrors real software development: build the minimum viable product, validate it works, then iterate. Perfect is the enemy of good, and good shipped beats perfect unfinished.
