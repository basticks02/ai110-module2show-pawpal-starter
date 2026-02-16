# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Get immersed:
[Try it yourself](https://bastickspawpalstarter.streamlit.app/)


## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors



## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

### Run the CLI Demo

```bash
python main.py
```

---

## Features Implemented

### Core Functionality
- ✅ **Multi-pet management** - Add/remove multiple pets (dogs, cats, rabbits, birds)
- ✅ **Task management** - Create tasks with priority (CRITICAL/HIGH/MEDIUM/LOW) and categories
- ✅ **Smart scheduling** - Priority-based greedy algorithm with time constraints
- ✅ **Detailed explanations** - Every scheduled task includes reasoning
- ✅ **Utilization metrics** - Track how efficiently you use available time

### Algorithmic Intelligence (Phase 4)
- ✅ **Recurring tasks** - Daily/weekly/monthly tasks auto-generate next occurrence
- ✅ **Task completion tracking** - Mark tasks complete and filter by status
- ✅ **Flexible sorting** - Sort by priority, duration, or category
- ✅ **Advanced filtering** - Filter by completion status, priority, or category
- ✅ **Conflict detection** - Detailed warnings for overlapping time slots

### User Interface
- ✅ **Step-by-step workflow** - Guided 4-step process
- ✅ **Color-coded priorities** - 🔴 CRITICAL, 🟠 HIGH, 🟡 MEDIUM, 🟢 LOW
- ✅ **Time slot display** - Clear HH:MM - HH:MM format
- ✅ **Responsive design** - Wide layout for better space usage
- ✅ **Real-time feedback** - Success/warning messages and validation

---

## System Architecture

### Classes Implemented

**Domain Models:**
- `Task` - Pet care activity with duration, priority, category, frequency
- `Pet` - Pet entity with task collection and management methods
- `Owner` - Owner with time budget, pets, and preferences
- `OwnerPreferences` - Scheduling preferences and constraints

**Scheduling System:**
- `Scheduler` (abstract) - Base interface for scheduling algorithms
- `PriorityGreedyScheduler` - Priority-based greedy scheduling implementation
- `Schedule` - Output with scheduled/unscheduled tasks and metrics
- `ScheduledTask` - Task with time slot and reasoning

**Enumerations:**
- `Priority` - LOW (1), MEDIUM (2), HIGH (3), CRITICAL (4)
- `TaskCategory` - WALK, FEEDING, MEDICATION, GROOMING, ENRICHMENT
- `TaskFrequency` - ONCE, DAILY, WEEKLY, MONTHLY

See [uml.md](uml.md) for the complete UML diagram.

---

## Testing PawPal+

### Automated Test Suite

The project includes 29+ comprehensive tests covering:

**Unit Tests:**
- Task creation, priority scoring, and completion tracking
- Pet task management (add, remove, filter, sort)
- Owner multi-pet aggregation and time calculations
- Schedule validation, conflict detection, and explanations
- Scheduler priority ordering and constraint handling

**Algorithmic Tests:**
- Recurring task generation (daily tasks auto-create next occurrence)
- Completion status filtering (incomplete vs completed tasks)
- Sorting by priority and duration
- Multi-pet task aggregation
- Detailed conflict detection with time slot information

**Edge Case Tests:**
- Empty task lists → valid empty schedules
- Zero available time → all tasks unscheduled with explanation
- Insufficient time → highest priority tasks scheduled first
- All same priority → correct tiebreaking (category, duration, alphabetical)
- Overlapping time slots → conflict detection and warnings

### Run Tests

```bash
# Run all tests
python -m pytest tests/test_pawpal.py -v

# Run with coverage (requires pytest-cov)
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

### Manual Test Verification

```bash
# Quick verification of core functionality
python main.py
```

This runs a comprehensive demo showing:
- Schedule generation with 2 pets (dog and cat)
- 7 tasks with varying priorities
- Algorithmic features (sorting, filtering, recurring tasks)
- Conflict detection
- Detailed explanations

### Test Results

**Status:** ✅ All tests passing
**Test Coverage:** 29+ test cases
**Confidence Level:** ⭐⭐⭐⭐⭐ (5/5)

**What's tested:**
- ✅ Core scheduling logic with multiple scenarios
- ✅ Priority-based task ordering (CRITICAL → HIGH → MEDIUM → LOW)
- ✅ Time budget constraints and utilization calculations
- ✅ Recurring task automation
- ✅ Completion tracking and filtering
- ✅ Conflict detection with detailed reporting
- ✅ Edge cases (empty lists, zero time, insufficient time)
- ✅ Multi-pet scheduling fairness

**Confidence Rationale:**
The system has been thoroughly tested with unit tests, integration tests, and edge case coverage. The greedy scheduling algorithm is deterministic and produces consistent results. All core features (scheduling, sorting, filtering, conflict detection) have been validated through automated and manual testing.

---

## Project Structure

```
ai110-module2show-pawpal-starter/
├── app.py                    # Streamlit UI (350+ lines)
├── main.py                   # CLI demo script
├── uml.md                    # UML class diagram (Mermaid)
├── reflection.md             # Project reflection and learnings
├── requirements.txt          # Python dependencies
├── src/
│   └── pawpal_system.py     # Core backend logic (400+ lines)
└── tests/
    └── test_pawpal.py       # Comprehensive test suite (450+ lines)
```

---

## Key Design Decisions

1. **Separation of Concerns** - Domain models separate from scheduling logic
2. **Strategy Pattern** - Abstract Scheduler allows multiple algorithms
3. **Rich Explanations** - Every decision includes human-readable reasoning
4. **Extensibility** - Easy to add new schedulers, priorities, or categories
5. **Testability** - Pure functions and small, focused methods

See [reflection.md](reflection.md) for detailed design rationale and tradeoffs.
