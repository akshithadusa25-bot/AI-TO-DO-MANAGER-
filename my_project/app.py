import streamlit as st
import sqlite3
from datetime import date


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="AI To-Do Manager",
    page_icon="🤖"
)

st.title("🤖 AI To-Do Manager")
st.write("Manage your tasks easily!")


# =========================================================
# DATABASE
# =========================================================

def get_connection():
    return sqlite3.connect("todo.db")


def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            priority TEXT DEFAULT 'Medium',
            due_date TEXT DEFAULT ''
        )
    """)

    conn.commit()
    conn.close()


create_database()


# =========================================================
# DATABASE FUNCTIONS
# =========================================================

def get_tasks():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, task, completed, priority, due_date
        FROM tasks
        ORDER BY id DESC
    """)

    tasks = cursor.fetchall()

    conn.close()

    return tasks


def add_task(task, priority, due_date):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks
        (task, completed, priority, due_date)
        VALUES (?, ?, ?, ?)
    """, (task, 0, priority, due_date))

    conn.commit()
    conn.close()


def update_task(task_id, completed):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET completed = ?
        WHERE id = ?
    """, (int(completed), task_id))

    conn.commit()
    conn.close()


def edit_task(task_id, new_task, new_priority, new_due_date):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET task = ?,
            priority = ?,
            due_date = ?
        WHERE id = ?
    """, (
        new_task,
        new_priority,
        new_due_date,
        task_id
    ))

    conn.commit()
    conn.close()


def delete_task(task_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()


# =========================================================
# ADD TASK
# =========================================================

st.header("➕ Add a Task")

task = st.text_input(
    "Enter your task",
    placeholder="Example: Study Python"
)

col1, col2 = st.columns(2)

with col1:

    priority = st.selectbox(
        "⭐ Priority",
        ["Low", "Medium", "High"]
    )

with col2:

    add_due_date = st.checkbox(
        "📅 Add due date"
    )

    if add_due_date:

        selected_date = st.date_input(
            "Due date",
            min_value=date.today()
        )

        due_date = selected_date.strftime("%Y-%m-%d")

    else:

        due_date = ""


if st.button("Add Task"):

    if task.strip():

        add_task(
            task.strip(),
            priority,
            due_date
        )

        st.success("Task added successfully!")

        st.rerun()

    else:

        st.warning("Please enter a task.")


# =========================================================
# MY TASKS
# =========================================================

st.header("📋 My Tasks")

tasks = get_tasks()


if len(tasks) == 0:

    st.info("No tasks yet. Add your first task!")

else:

    for (
        task_id,
        task_text,
        completed,
        priority_value,
        due_date_value
    ) in tasks:

        col1, col2, col3 = st.columns([7, 1, 1])


        # -------------------------------------------------
        # CHECKBOX
        # -------------------------------------------------

        with col1:

            checked = st.checkbox(
                task_text,
                value=bool(completed),
                key=f"check_{task_id}"
            )

            if checked != bool(completed):

                update_task(
                    task_id,
                    checked
                )

                st.rerun()


        # -------------------------------------------------
        # EDIT BUTTON
        # -------------------------------------------------

        with col2:

            edit_clicked = st.button(
                "✏️",
                key=f"edit_{task_id}"
            )


        # -------------------------------------------------
        # DELETE BUTTON
        # -------------------------------------------------

        with col3:

            delete_clicked = st.button(
                "🗑️",
                key=f"delete_{task_id}"
            )

            if delete_clicked:

                delete_task(task_id)

                st.success("Task deleted!")

                st.rerun()


        # -------------------------------------------------
        # PRIORITY + DUE DATE
        # -------------------------------------------------

        priority_icons = {
            "High": "🔴",
            "Medium": "🟡",
            "Low": "🟢"
        }

        icon = priority_icons.get(
            priority_value,
            "🟡"
        )

        if due_date_value:

            st.caption(
                f"{icon} {priority_value} Priority"
                f"  |  📅 Due: {due_date_value}"
            )

        else:

            st.caption(
                f"{icon} {priority_value} Priority"
                f"  |  📅 No due date"
            )


        # -------------------------------------------------
        # EDIT FORM
        # -------------------------------------------------

        if edit_clicked:

            st.subheader("✏️ Edit Task")

            edited_task = st.text_input(
                "Task",
                value=task_text,
                key=f"edit_task_{task_id}"
            )

            priorities = [
                "Low",
                "Medium",
                "High"
            ]

            edited_priority = st.selectbox(
                "⭐ Priority",
                priorities,
                index=priorities.index(
                    priority_value
                ),
                key=f"edit_priority_{task_id}"
            )

            has_due_date = bool(
                due_date_value
            )

            edit_due_enabled = st.checkbox(
                "📅 Set due date",
                value=has_due_date,
                key=f"edit_due_{task_id}"
            )

            if edit_due_enabled:

                if due_date_value:

                    existing_date = date.fromisoformat(
                        due_date_value
                    )

                else:

                    existing_date = date.today()

                edited_date = st.date_input(
                    "Due date",
                    value=existing_date,
                    key=f"edit_date_{task_id}"
                )

                edited_due_date = edited_date.strftime(
                    "%Y-%m-%d"
                )

            else:

                edited_due_date = ""


            save_col, cancel_col = st.columns(2)

            with save_col:

                if st.button(
                    "💾 Save Changes",
                    key=f"save_{task_id}"
                ):

                    if edited_task.strip():

                        edit_task(
                            task_id,
                            edited_task.strip(),
                            edited_priority,
                            edited_due_date
                        )

                        st.success(
                            "Task updated successfully!"
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "Task cannot be empty."
                        )


            with cancel_col:

                if st.button(
                    "❌ Cancel",
                    key=f"cancel_{task_id}"
                ):

                    st.rerun()