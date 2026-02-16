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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
