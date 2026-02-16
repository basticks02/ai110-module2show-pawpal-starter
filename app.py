"""
PawPal+ Streamlit App
Pet care task scheduling assistant with intelligent priority-based scheduling.
"""

import streamlit as st
from datetime import date
from src.pawpal_system import (
    Task, Pet, Owner, OwnerPreferences,
    Priority, TaskCategory,
    PriorityGreedyScheduler
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# Initialize session state
if "owner" not in st.session_state:
    st.session_state.owner = None

if "current_schedule" not in st.session_state:
    st.session_state.current_schedule = None

# ============================================================================
# Header
# ============================================================================

st.title("🐾 PawPal+")
st.markdown("**Smart pet care task scheduling assistant**")
st.caption("Plan your daily pet care tasks based on time constraints and priorities")

st.divider()

# ============================================================================
# Step 1: Owner Setup
# ============================================================================

st.header("1️⃣ Owner Setup")

with st.expander("Owner Information", expanded=(st.session_state.owner is None)):
    col1, col2 = st.columns(2)

    with col1:
        owner_name = st.text_input("Owner Name", value="Jordan", help="Your name")

    with col2:
        available_time = st.number_input(
            "Available Time (minutes)",
            min_value=0,
            max_value=480,
            value=120,
            step=15,
            help="How many minutes you have for pet care today"
        )

    if st.button("Create/Update Owner", type="primary"):
        st.session_state.owner = Owner(
            name=owner_name,
            available_time_minutes=available_time
        )
        st.session_state.current_schedule = None  # Reset schedule
        st.success(f"✅ Owner '{owner_name}' created with {available_time} minutes available")
        st.rerun()

if st.session_state.owner:
    st.info(f"👤 **Owner:** {st.session_state.owner.name} | ⏰ **Available Time:** {st.session_state.owner.available_time_minutes} minutes")

st.divider()

# ============================================================================
# Step 2: Pet Management
# ============================================================================

st.header("2️⃣ Pet Management")

if st.session_state.owner is None:
    st.warning("⚠️ Please create an owner first before adding pets.")
else:
    # Add Pet Section
    with st.expander("Add a Pet", expanded=(len(st.session_state.owner.pets) == 0)):
        col1, col2, col3 = st.columns(3)

        with col1:
            pet_name = st.text_input("Pet Name", value="Mochi", key="new_pet_name")

        with col2:
            pet_species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"], key="new_pet_species")

        with col3:
            pet_age = st.number_input("Age (years)", min_value=0.0, max_value=30.0, value=3.5, step=0.5, key="new_pet_age")

        if st.button("Add Pet", type="primary"):
            new_pet = Pet(
                name=pet_name,
                species=pet_species,
                age_years=pet_age
            )
            st.session_state.owner.add_pet(new_pet)
            st.session_state.current_schedule = None  # Reset schedule
            st.success(f"✅ Added {pet_species} '{pet_name}' ({pet_age} years old)")
            st.rerun()

    # Display Current Pets
    if len(st.session_state.owner.pets) > 0:
        st.subheader("Your Pets")

        for idx, pet in enumerate(st.session_state.owner.pets):
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                with col1:
                    icon = {"dog": "🐕", "cat": "🐈", "rabbit": "🐰", "bird": "🦜", "other": "🐾"}.get(pet.species, "🐾")
                    st.write(f"{icon} **{pet.name}** ({pet.species}, {pet.age_years} years)")

                with col2:
                    st.write(f"📋 {len(pet.tasks)} tasks")

                with col3:
                    total_time = sum(t.duration_minutes for t in pet.tasks)
                    st.write(f"⏱️ {total_time} min")

                with col4:
                    if st.button(f"Remove", key=f"remove_pet_{idx}"):
                        st.session_state.owner.remove_pet(pet)
                        st.session_state.current_schedule = None
                        st.rerun()

        st.divider()

        # ============================================================================
        # Step 3: Task Management
        # ============================================================================

        st.header("3️⃣ Task Management")

        # Select which pet to add task to
        pet_names = [p.name for p in st.session_state.owner.pets]
        selected_pet_name = st.selectbox("Add task for:", pet_names, key="selected_pet_for_task")
        selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)

        with st.expander("Add a Task", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                task_title = st.text_input("Task Title", value="Morning walk", key="new_task_title")

                task_priority = st.selectbox(
                    "Priority",
                    ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                    index=2,
                    key="new_task_priority",
                    help="CRITICAL: Must do | HIGH: Important | MEDIUM: Should do | LOW: Nice to have"
                )

            with col2:
                task_duration = st.number_input(
                    "Duration (minutes)",
                    min_value=1,
                    max_value=240,
                    value=30,
                    step=5,
                    key="new_task_duration"
                )

                task_category = st.selectbox(
                    "Category",
                    ["WALK", "FEEDING", "MEDICATION", "GROOMING", "ENRICHMENT"],
                    index=0,
                    key="new_task_category"
                )

            task_description = st.text_area(
                "Description (optional)",
                placeholder="Add details about this task...",
                key="new_task_description"
            )

            if st.button("Add Task", type="primary"):
                new_task = Task(
                    title=task_title,
                    duration_minutes=task_duration,
                    priority=Priority[task_priority],
                    category=TaskCategory[task_category],
                    description=task_description
                )
                selected_pet.add_task(new_task)
                st.session_state.current_schedule = None  # Reset schedule
                st.success(f"✅ Added task '{task_title}' to {selected_pet.name}")
                st.rerun()

        # Display tasks for all pets
        st.subheader("All Tasks")

        for pet in st.session_state.owner.pets:
            if len(pet.tasks) > 0:
                st.markdown(f"**{pet.name}'s Tasks:**")

                for task_idx, task in enumerate(pet.tasks):
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

                        with col1:
                            priority_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
                            st.write(f"{priority_emoji.get(task.priority.name, '⚪')} {task.title}")

                        with col2:
                            st.write(f"{task.duration_minutes} min")

                        with col3:
                            st.write(task.priority.name)

                        with col4:
                            st.write(task.category.value)

                        with col5:
                            if st.button("Remove", key=f"remove_task_{pet.name}_{task_idx}"):
                                pet.remove_task(task)
                                st.session_state.current_schedule = None
                                st.rerun()
            else:
                st.info(f"No tasks yet for {pet.name}")

        # Show summary
        all_tasks = st.session_state.owner.get_all_tasks()
        total_task_time = st.session_state.owner.calculate_total_task_time()

        if len(all_tasks) > 0:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Tasks", len(all_tasks))

            with col2:
                st.metric("Total Time Needed", f"{total_task_time} min")

            with col3:
                if total_task_time > st.session_state.owner.available_time_minutes:
                    st.metric(
                        "Time Status",
                        "⚠️ Over budget",
                        f"+{total_task_time - st.session_state.owner.available_time_minutes} min"
                    )
                else:
                    st.metric(
                        "Time Status",
                        "✅ Under budget",
                        f"-{st.session_state.owner.available_time_minutes - total_task_time} min"
                    )

        st.divider()

        # ============================================================================
        # Step 4: Generate Schedule
        # ============================================================================

        st.header("4️⃣ Generate Schedule")

        if len(all_tasks) == 0:
            st.warning("⚠️ Please add at least one task before generating a schedule.")
        else:
            col1, col2, col3 = st.columns([2, 1, 2])

            with col2:
                if st.button("🗓️ Generate Schedule", type="primary", use_container_width=True):
                    scheduler = PriorityGreedyScheduler(st.session_state.owner, date.today())
                    st.session_state.current_schedule = scheduler.generate_schedule()
                    st.success("✅ Schedule generated!")
                    st.rerun()

        # ============================================================================
        # Step 5: Display Schedule
        # ============================================================================

        if st.session_state.current_schedule:
            st.divider()
            st.header("📅 Your Daily Schedule")

            schedule = st.session_state.current_schedule

            # Schedule Metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Scheduled Tasks", len(schedule.scheduled_tasks))

            with col2:
                st.metric("Unscheduled Tasks", len(schedule.unscheduled_tasks))

            with col3:
                st.metric("Total Time", f"{schedule.total_time_minutes} min")

            with col4:
                st.metric("Utilization", f"{schedule.utilization_percentage}%")

            # Scheduled Tasks
            if len(schedule.scheduled_tasks) > 0:
                st.subheader("⏰ Scheduled Tasks")

                for st_task in schedule.scheduled_tasks:
                    end_time = st_task.get_end_time()

                    with st.container():
                        col1, col2, col3 = st.columns([1, 2, 3])

                        with col1:
                            st.markdown(f"**{st_task.scheduled_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}**")

                        with col2:
                            priority_color = {
                                "CRITICAL": "🔴",
                                "HIGH": "🟠",
                                "MEDIUM": "🟡",
                                "LOW": "🟢"
                            }
                            st.markdown(f"{priority_color.get(st_task.task.priority.name, '⚪')} **{st_task.task.title}**")
                            st.caption(f"{st_task.task.duration_minutes} min • {st_task.task.priority.name} • {st_task.task.category.value}")

                        with col3:
                            st.info(f"💡 {st_task.reasoning}")

            else:
                st.info("No tasks were scheduled. This might be due to insufficient time or no tasks available.")

            # Unscheduled Tasks
            if len(schedule.unscheduled_tasks) > 0:
                st.subheader("❌ Unscheduled Tasks")
                st.caption("These tasks could not fit in your available time")

                for task in schedule.unscheduled_tasks:
                    with st.container():
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            priority_color = {
                                "CRITICAL": "🔴",
                                "HIGH": "🟠",
                                "MEDIUM": "🟡",
                                "LOW": "🟢"
                            }
                            st.markdown(f"{priority_color.get(task.priority.name, '⚪')} **{task.title}**")
                            st.caption(f"{task.duration_minutes} min • {task.priority.name} • {task.category.value}")

                        with col2:
                            if task.priority == Priority.CRITICAL:
                                st.warning("⚠️ Critical!")

            # Schedule Explanation
            with st.expander("📝 Schedule Explanation", expanded=False):
                st.write(schedule.generate_explanation())

            # Validation Status
            is_valid = schedule.validate()
            if is_valid:
                st.success("✅ Schedule is valid (no time conflicts detected)")
            else:
                st.error("❌ Schedule has conflicts! Please review.")

    else:
        st.info("👆 Add a pet to get started")

# ============================================================================
# Footer
# ============================================================================

st.divider()
st.caption("🐾 PawPal+ • Smart Pet Care Scheduling • Built with Streamlit")
