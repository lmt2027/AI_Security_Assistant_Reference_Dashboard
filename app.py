
"""AI Security Assistant — Streamlit Capstone Dashboard.

Uses synthetic security events stored in SQLite.
AI responses require an OpenAI API key with available credits.
"""

import html
import textwrap
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

try:
    initialize_demo_database()

except (FileNotFoundError, RuntimeError) as error:
    st.error(str(error))
    st.warning(
        "The application has stopped to protect "
        "your existing security records."
    )
    st.stop()

from database import (
    create_database,
    get_detected_alerts,
    get_reviews,
    save_detected_alert,
    save_review,
    seed_demo_alerts,
    create_response_tables,
    add_response_action,
    update_response_action,
    get_response_actions,
    create_event_tables,
    seed_security_events,
    get_security_events,
)
from securitychecker import check_failed_logins
from event_detection import analyze_database_events
from ai_assistant import ask_ai, get_api_key, DEFAULT_MODEL


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Security Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)



# ============================================================
# DATABASE INITIALIZATION WITH FAILURE PROTECTION
# ============================================================

import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "security_assistant.db"

# Check that the original database exists before initializing.
if not DATABASE_PATH.is_file():
    st.error("Database unavailable: security_assistant.db was not found.")
    st.warning(
        "The application has stopped to prevent a new empty database "
        "from silently replacing your saved security records."
    )
    st.info(
        "To recover: stop Streamlit, restore security_assistant.db "
        "from your backup, and restart the application."
    )
    st.stop()

# Verify that the file is a readable SQLite database.
try:
    connection = sqlite3.connect(
        f"{DATABASE_PATH.as_uri()}?mode=ro",
        uri=True,
        timeout=5,
    )

    try:
        result = connection.execute("PRAGMA quick_check").fetchone()
        if result is None or result[0] != "ok":
            raise sqlite3.DatabaseError("Database integrity check failed.")

        required_tables = {
            "reviews",
            "detected_alerts",
            "security_events",
            "response_actions",
        }

        existing_tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }

        missing_tables = required_tables - existing_tables

        if missing_tables:
            raise sqlite3.DatabaseError(
                "Required database tables are missing: "
                + ", ".join(sorted(missing_tables))
            )

    finally:
        connection.close()

except (sqlite3.Error, OSError) as error:
    st.error("The security database could not be validated.")
    st.warning(
        "The dashboard has been stopped to protect your saved records."
    )
    st.code(str(error))
    st.info(
        "Restore a verified backup of security_assistant.db "
        "and restart Streamlit."
    )
    st.stop()

# Only initialize the application after validation succeeds.
try:
    create_database()
    seed_demo_alerts()
    create_event_tables()
    seed_security_events()
    create_response_tables()

except (sqlite3.Error, OSError) as error:
    st.error("Database initialization failed.")
    st.code(str(error))
    st.stop()



# ============================================================
# HTML HELPER — FIXES RAW HTML DISPLAYING AS TEXT
# ============================================================

def render_html(markup):
    """Render dashboard HTML without Markdown indentation problems."""
    st.markdown(
        textwrap.dedent(markup).strip(),
        unsafe_allow_html=True,
    )


def safe(value):
    """Escape dynamic text before inserting it into HTML."""
    return html.escape(str(value))


# ============================================================
# DASHBOARD STYLING
# ============================================================

st.markdown(
    """
<style>
:root {
    --navy: #102748;
    --blue: #1975e9;
}

[data-testid="stAppViewContainer"] {
    background: #f4f7fc !important;
}

/* Make the dashboard fill the available screen width */
.block-container,
[data-testid="stMainBlockContainer"] {
    max-width: 100% !important;
    width: 100% !important;
    padding-top: 5.25rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #102e52 0%,
        #102746 60%,
        #0c2340 100%
    ) !important;
    min-width: 205px;
}

[data-testid="stSidebar"] * {
    color: #f4f8ff !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 9px;
    margin: 2px 0;
    padding: 9px 12px !important;
}

[data-testid="stSidebar"]
[role="radiogroup"] label:has(input:checked) {
    background: #2068cf !important;
}

h1, h2, h3 {
    color: #102748 !important;
    letter-spacing: -0.025em;
}

button[kind="primary"] {
    background: #176de0 !important;
}

/* Prevent horizontal overflow */
[data-testid="stHorizontalBlock"],
[data-testid="stColumn"] {
    min-width: 0 !important;
}

[data-testid="stMarkdownContainer"] {
    overflow-wrap: anywhere;
}

[data-testid="stChatMessageContent"] {
    min-width: 0;
    overflow-wrap: anywhere;
}

[data-testid="stChatMessageContent"] table {
    display: block;
    max-width: 100%;
    overflow-x: auto;
}

/* Main header */
.reference-header {
    background: linear-gradient(95deg, #102849, #194c7b);
    border-radius: 12px;
    padding: 18px 22px;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
    margin: 0 0 20px;
    min-height: 85px;
}

.reference-brand {
    font-size: 23px;
    font-weight: 800;
    line-height: 1.2;
    color: white;
}

.reference-sub {
    font-size: 12px;
    color: #e4efff;
    margin-top: 5px;
}

.reference-status {
    font-size: 12px;
    color: #b9f7d5;
    white-space: nowrap;
}

/* Greeting */
.reference-greeting {
    font-size: 26px;
    font-weight: 800;
    color: #0e2850;
    letter-spacing: -0.03em;
    margin: 4px 0;
}

.reference-greeting-sub {
    color: #405a79;
    font-size: 13px;
    margin: 5px 0 18px;
}

/* Summary cards */
.reference-stat {
    border-radius: 10px;
    border: 1px solid var(--line);
    background: var(--bg);
    padding: 16px 13px;
    min-height: 110px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.reference-stat-icon {
    background: var(--accent);
    color: white;
    width: 45px;
    height: 45px;
    flex: 0 0 45px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 50%;
    font-size: 25px;
    font-weight: 800;
}

.reference-stat-number {
    color: #10284c;
    font-size: 30px;
    line-height: 1;
    font-weight: 800;
}

.reference-stat-label {
    color: var(--accent);
    font-size: 13px;
    font-weight: 800;
    margin-top: 3px;
}

.reference-stat-note {
    font-size: 11px;
    color: #465a77;
    margin-top: 3px;
}

/* Section headings */
.reference-section {
    font-size: 18px;
    font-weight: 800;
    color: #10284c;
    margin: 0 0 4px;
}

.reference-section-sub {
    font-size: 12px;
    color: #5d708b;
    margin: 0 0 12px;
}

/* Security alert cards */
.reference-alert {
    border: 1px solid var(--line);
    background: var(--bg);
    border-radius: 9px;
    padding: 12px;
    display: flex;
    gap: 12px;
    align-items: center;
    min-height: 100px;
    margin: 0 0 6px;
}

.reference-alert-icon {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background: var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
    flex: 0 0 46px;
}

.reference-alert-content {
    min-width: 0;
    flex: 1;
}

.reference-alert-title {
    font-size: 14px;
    font-weight: 800;
    color: #0d2a50;
}

.reference-alert-desc {
    font-size: 12px;
    line-height: 1.5;
    color: #385071;
    margin-top: 4px;
}

.reference-alert-badge {
    font-size: 11px;
    font-weight: 750;
    background: var(--tag);
    color: var(--accent);
    padding: 5px 8px;
    border-radius: 6px;
    display: inline-block;
}

.reference-alert-date {
    font-size: 10px;
    color: #516985;
    margin-top: 6px;
}

/* Bottom panels */
.reference-panel-title {
    font-size: 15px;
    font-weight: 800;
    color: #10284c;
    margin: 0 0 5px;
}

.reference-mini {
    font-size: 12px;
    color: #506785;
    line-height: 1.6;
}

.reference-area {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    border-bottom: 1px solid #e8eef6;
    padding: 7px 0;
    font-size: 12px;
    color: #243e5e;
}

.reference-area span:last-child {
    background: #e8f0ff;
    color: #1456bb;
    padding: 1px 9px;
    border-radius: 30px;
    font-weight: 800;
}

/* AI panel */
.chat-bubble {
    background: #f1f6fe;
    border: 1px solid #e0eafb;
    border-radius: 10px;
    padding: 12px;
    font-size: 13px;
    color: #193457;
    line-height: 1.6;
    margin: 10px 0;
}

.section-head {
    color: #102748;
    font-size: 20px;
    font-weight: 750;
    margin: 6px 0 12px;
}

.st-key-home_open_chat button {
    background: #1168ee !important;
    color: white !important;
}

/* Responsive layout */
@media (max-width: 1000px) {
    .reference-status {
        white-space: normal;
    }

    .reference-stat {
        padding: 10px 8px;
    }

    .reference-stat-icon {
        width: 34px;
        height: 34px;
        flex-basis: 34px;
        font-size: 19px;
    }
}

@media (max-width: 640px) {
    .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-top: 5.5rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }

    .reference-header {
        flex-wrap: wrap;
    }

    .reference-brand {
        font-size: 20px;
    }
}

/* Keep sidebar visible on desktop */
@media (min-width: 768px) {

    [data-testid="stSidebar"] {
        transform: none !important;
        visibility: visible !important;
        min-width: 205px !important;
    }

    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# NAVIGATION
# ============================================================

PAGES = [
    "Home",
    "Security Alerts",
    "Security Checker",
    "Protection Tips",
    "Action History",
    "Response Plans",
    "Test Data",
    "Ask Assistant",
]

if "main_navigation" not in st.session_state:
    st.session_state.main_navigation = "Home"

if "navigation_target" in st.session_state:
    st.session_state.main_navigation = (
        st.session_state.pop("navigation_target")
    )

st.sidebar.markdown("## 🛡️ AI Security Assistant")
st.sidebar.caption("Your Partner for a Safer Business")
st.sidebar.divider()

page = st.sidebar.radio(
    "MAIN MENU",
    PAGES,
    key="main_navigation",
)

st.sidebar.divider()
st.sidebar.caption("SYNTHETIC DATA · No live monitoring")


def navigate(destination):
    st.session_state.navigation_target = destination
    st.rerun()


def priority_style(priority):
    styles = {
        "High": (
            "#fff0f1",
            "#f3cbd0",
            "#c72836",
            "#ffd9dd",
            "🔴",
        ),
        "Medium": (
            "#fff7e8",
            "#f5e4bc",
            "#ba6b00",
            "#ffe9b2",
            "🟠",
        ),
        "Low": (
            "#edf5ff",
            "#d5e7ff",
            "#2068ce",
            "#dbeaff",
            "🔵",
        ),
    }

    return styles.get(priority, styles["Low"])


# ============================================================
# AI ASSISTANT
# ============================================================

def render_assistant_panel():
    render_html(
        """
        <div class="section-head">
            🤖 AI Security Assistant
        </div>
        """
    )

    st.caption(
        "Online OpenAI API model · "
        "Answers use read-only synthetic SQLite records"
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    st.caption(f"🤖 Powered by OpenAI · {DEFAULT_MODEL}")

    if get_api_key():
        st.success("🟢 OpenAI API key configured")
        st.caption("Your AI Assistant is ready to test.")
    else:
        st.warning("🟠 OpenAI API key not configured")
        st.caption(
            "Add OPENAI_API_KEY to .streamlit/secrets.toml "
            "to connect your assistant."
        )

    for role, message in st.session_state.chat_history[-8:]:
        with st.chat_message(role):
            st.write(message)

    with st.form(
        f"assistant_form_{page}",
        clear_on_submit=True,
    ):
        question = st.text_input(
            "Ask a question",
            value=st.session_state.pop(
                "home_prefill_question",
                "",
            ),
            placeholder="What happened in the sample data?",
        )

        submitted = st.form_submit_button(
            "Ask AI",
            use_container_width=True,
        )

    if submitted and question.strip():
        history = st.session_state.chat_history[:]

        try:
            with st.spinner("Asking the AI assistant..."):
                answer = ask_ai(
                    question.strip(),
                    history=history,
                )

        except Exception as exc:
            st.error(
                f"Could not get an AI response: {exc}"
            )

        else:
            st.session_state.chat_history.extend(
                [
                    ("user", question.strip()),
                    ("assistant", answer),
                ]
            )
            st.rerun()

    st.caption("Suggested questions")

    suggestions = [
        (
            "What should I do first?",
            "Based on the saved sample alerts, "
            "what should I do first?",
        ),
        (
            "Summarize test data",
            "Summarize the patterns in the "
            "synthetic security event database.",
        ),
    ]

    for label, question in suggestions:
        if st.button(
            label,
            key=f"suggest_{page}_{label}",
            use_container_width=True,
        ):
            history = st.session_state.chat_history[:]

            try:
                with st.spinner("Asking the AI assistant..."):
                    answer = ask_ai(
                        question,
                        history=history,
                    )

            except Exception as exc:
                st.error(
                    f"Could not get an AI response: {exc}"
                )

            else:
                st.session_state.chat_history.extend(
                    [
                        ("user", question),
                        ("assistant", answer),
                    ]
                )
                st.rerun()


# ============================================================
# LOAD DATABASE RECORDS
# ============================================================

alerts = get_detected_alerts()
reviews = get_reviews()

reviewed_ids = {
    review[0]
    for review in reviews
}

reviewed_detected = sum(
    f"detected_{alert[0]}" in reviewed_ids
    for alert in alerts
)


# ============================================================
# HOME DASHBOARD
# ============================================================

if page == "Home":

    greeting_hour = datetime.now().hour

    if greeting_hour < 12:
        greeting = "Good morning"
    elif greeting_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    # Main header
    render_html(
        """
        <div class="reference-header">
            <div>
                <div class="reference-brand">
                    🛡️ AI Security Assistant
                </div>
                <div class="reference-sub">
                    Your Partner for a Safer Business
                </div>
            </div>
            <div class="reference-status">
                ● Demo system running · Synthetic data
            </div>
        </div>
        """
    )

    # Greeting
    render_html(
        f"""
        <div class="reference-greeting">
            {greeting}! 👋
        </div>
        <div class="reference-greeting-sub">
            Here is what is happening with your
            business security today. Review simulated
            warnings and ask the AI for guidance.
        </div>
        """
    )

    # Summary counts
    counts = {
        level: sum(
            str(alert[2]).lower() == level.lower()
            for alert in alerts
        )
        for level in ("High", "Medium", "Low")
    }

    stat_cards = [
        (
            "⚠",
            "High Priority",
            counts["High"],
            "Needs your attention",
            "#fff0f1",
            "#f8d3d7",
            "#e72d39",
        ),
        (
            "!",
            "Medium Priority",
            counts["Medium"],
            "Worth reviewing",
            "#fff7e9",
            "#f6e3bb",
            "#f58a08",
        ),
        (
            "i",
            "Low Priority",
            counts["Low"],
            "Keeping an eye on it",
            "#ecf5ff",
            "#d7e7fb",
            "#237df1",
        ),
        (
            "✓",
            "Reviewed",
            reviewed_detected,
            "Recorded review actions",
            "#eaf8f1",
            "#d1ebdf",
            "#15925e",
        ),
    ]

    stat_columns = st.columns(4, gap="small")

    for col, card in zip(stat_columns, stat_cards):
        (
            symbol,
            label,
            count,
            note,
            bg,
            line,
            accent,
        ) = card

        with col:
            render_html(
                f"""
                <div class="reference-stat"
                     style="--bg:{bg}; --line:{line}; --accent:{accent};">
                    <div class="reference-stat-icon">
                        {symbol}
                    </div>
                    <div>
                        <div class="reference-stat-number">
                            {count}
                        </div>
                        <div class="reference-stat-label">
                            {label}
                        </div>
                        <div class="reference-stat-note">
                            {note}
                        </div>
                    </div>
                </div>
                """
            )

    st.write("")

    main_col, assistant_col = st.columns(
        [3.1, 1],
        gap="medium",
    )

    # ========================================================
    # RECENT ALERTS
    # ========================================================

    with main_col:

        with st.container(border=True):

            render_html(
                """
                <div class="reference-section">
                    🔔 Recent Security Alerts
                </div>
                <div class="reference-section-sub">
                    Important simulated findings,
                    explained in everyday language
                    with recommended next steps.
                </div>
                """
            )

            for alert in alerts[:4]:

                (
                    alert_id,
                    title,
                    severity,
                    explanation,
                    recommendation,
                    attempts,
                    detected_at,
                ) = alert

                bg, line, accent, tag, symbol = (
                    priority_style(severity)
                )

                details, action = st.columns(
                    [4.2, 1.05],
                    gap="small",
                    vertical_alignment="center",
                )

                with details:
                    render_html(
                        f"""
                        <div class="reference-alert"
                             style="--bg:{bg}; --line:{line}; --accent:{accent}; --tag:{tag};">
                            <div class="reference-alert-icon">
                                {symbol}
                            </div>
                            <div class="reference-alert-content">
                                <div class="reference-alert-title">
                                    {safe(title)}
                                </div>
                                <div class="reference-alert-desc">
                                    {safe(explanation)}
                                </div>
                                <div class="reference-alert-date">
                                    {safe(detected_at)}
                                </div>
                            </div>
                        </div>
                        """
                    )

                with action:

                    render_html(
                        f"""
                        <span class="reference-alert-badge"
                              style="--tag:{tag}; --accent:{accent};">
                            {safe(severity)} Priority
                        </span>
                        """
                    )

                    if st.button(
                        "Review & Act →",
                        key=f"home_alert_{alert_id}",
                        use_container_width=True,
                    ):
                        st.session_state[
                            "focus_alert"
                        ] = alert_id
                        navigate("Security Alerts")

            if st.button(
                "View All Alerts →",
                key="all_alerts",
            ):
                navigate("Security Alerts")

        # ====================================================
        # BOTTOM DASHBOARD PANELS
        # ====================================================

        trend_col, areas_col, actions_col = st.columns(
            [1.2, 1.05, 1.05],
            gap="small",
        )

        # Security trend
        with trend_col:

            with st.container(border=True):

                render_html(
                    """
                    <div class="reference-panel-title">
                        📊 Your Security Trend
                    </div>
                    <div class="reference-mini">
                        Saved alerts over the last seven days
                    </div>
                    """
                )

                dates = [
                    datetime.now().date()
                    - timedelta(days=i)
                    for i in range(6, -1, -1)
                ]

                by_date = {
                    day: 0
                    for day in dates
                }

                for alert in alerts:
                    try:
                        day = pd.to_datetime(
                            alert[6]
                        ).date()

                        if day in by_date:
                            by_date[day] += 1

                    except (ValueError, TypeError):
                        pass

                chart_df = pd.DataFrame(
                    {
                        "Date": pd.to_datetime(dates),
                        "Warnings": [
                            by_date[day]
                            for day in dates
                        ],
                    }
                )

                st.line_chart(
                    chart_df,
                    x="Date",
                    y="Warnings",
                    height=210,
                )

        # Most affected areas
        with areas_col:

            with st.container(border=True):

                render_html(
                    """
                    <div class="reference-panel-title">
                        ◕ Most Affected Areas
                    </div>
                    <div class="reference-mini">
                        Grouped by warning type
                    </div>
                    """
                )

                categories = {
                    "Employee Accounts": 0,
                    "Computers & Devices": 0,
                    "Business Software": 0,
                    "Other": 0,
                }

                for alert in alerts:

                    name = alert[1].lower()

                    if any(
                        word in name
                        for word in (
                            "login",
                            "sign-in",
                            "password",
                            "employee",
                            "account",
                        )
                    ):
                        categories["Employee Accounts"] += 1

                    elif any(
                        word in name
                        for word in (
                            "computer",
                            "device",
                            "endpoint",
                        )
                    ):
                        categories["Computers & Devices"] += 1

                    elif any(
                        word in name
                        for word in (
                            "software",
                            "program",
                            "update",
                        )
                    ):
                        categories["Business Software"] += 1

                    else:
                        categories["Other"] += 1

                for category, count in categories.items():

                    render_html(
                        f"""
                        <div class="reference-area">
                            <span>
                                {safe(category)}
                            </span>
                            <span>
                                {count}
                            </span>
                        </div>
                        """
                    )

        # Quick actions
        with actions_col:

            with st.container(border=True):

                render_html(
                    """
                    <div class="reference-panel-title">
                        ⚡ Quick Actions
                    </div>
                    <div class="reference-mini">
                        Common security tasks
                    </div>
                    """
                )

                quick_actions = [
                    (
                        "🔐 Check Passwords",
                        "Security Checker",
                    ),
                    (
                        "🛡️ Response Plans",
                        "Response Plans",
                    ),
                    (
                        "👥 Review Accounts",
                        "Security Alerts",
                    ),
                    (
                        "💡 Security Tips",
                        "Protection Tips",
                    ),
                ]

                for label, target in quick_actions:

                    if st.button(
                        label,
                        key=f"quick_{target}_{label}",
                        use_container_width=True,
                    ):
                        navigate(target)

        # Review progress
        with st.expander("Alert review progress"):

            progress = (
                reviewed_detected / len(alerts)
                if alerts
                else 0
            )

            st.progress(progress)

            st.caption(
                f"{reviewed_detected} of {len(alerts)} "
                "warnings reviewed. "
                "Reviewed does not mean resolved."
            )

    # ========================================================
    # HOME AI ASSISTANT PANEL
    # ========================================================

    with assistant_col:

        with st.container(border=True):

            render_html(
                """
                <div class="reference-panel-title">
                    🤖 AI Security Assistant
                </div>
                <div class="reference-mini">
                    Ask questions, get clear answers,
                    and receive guidance in plain language.
                </div>
                """
            )

            st.divider()

            render_html(
                """
                <div class="chat-bubble">
                    👋 Hello! I can help explain your
                    simulated security alerts,
                    prioritize concerns, and suggest
                    practical next steps.
                </div>
                """
            )

            # Display the OpenAI model and connection status
            st.caption(f"🤖 Powered by OpenAI · {DEFAULT_MODEL}")

            if get_api_key():
                st.success("🟢 OpenAI API key configured")
            else:
                st.warning("🟠 OpenAI API key not configured")

            render_html(
                """
                <div class="reference-mini">
                    Try asking:
                </div>
                """
            )

            home_suggestions = [
                (
                    "What happened today?",
                    "Summarize the latest saved demo alerts.",
                ),
                (
                    "What should I do first?",
                    "Which saved demo alert needs "
                    "attention first and why?",
                ),
                (
                    "How can I be safer?",
                    "Suggest three practical steps "
                    "for a small business based "
                    "on my sample alerts.",
                ),
            ]

            for label, question in home_suggestions:

                if st.button(
                    label,
                    key=f"home_suggest_{label}",
                    use_container_width=True,
                ):
                    st.session_state[
                        "home_prefill_question"
                    ] = question
                    navigate("Ask Assistant")

            if st.button(
                "💬 Open Full AI Chat",
                key="home_open_chat",
                type="primary",
                use_container_width=True,
            ):
                navigate("Ask Assistant")

            st.caption(
                "Full AI conversations appear on "
                "the Ask Assistant page to prevent "
                "layout overflow."
            )


# ============================================================
# SECURITY ALERTS
# ============================================================

elif page == "Security Alerts":

    st.title("🔔 Security Alerts")

    st.caption(
        "Review saved demonstration warnings. "
        "Marking a warning reviewed does not "
        "fix the underlying problem."
    )

    severity_filter = st.selectbox(
        "Filter by priority",
        ["All", "High", "Medium", "Low"],
    )

    review_filter = st.selectbox(
        "Filter by review status",
        ["All", "Needs Review", "Reviewed"],
    )

    search = st.text_input(
        "Search alert titles",
        placeholder="e.g. password",
    )

    filtered = [
        alert
        for alert in alerts
        if (
            severity_filter == "All"
            or alert[2] == severity_filter
        )
        and (
            review_filter == "All"
            or (
                f"detected_{alert[0]}" in reviewed_ids
            ) == (review_filter == "Reviewed")
        )
        and search.lower() in alert[1].lower()
    ]

    st.caption(
        f"Showing {len(filtered)} of {len(alerts)} alerts"
    )

    if not filtered:
        st.info("No warnings match these filters.")

    for alert in filtered:

        (
            alert_id,
            title,
            severity,
            explanation,
            recommendation,
            attempts,
            detected_at,
        ) = alert

        review_id = f"detected_{alert_id}"

        icon = (
            "✅"
            if review_id in reviewed_ids
            else "⚠️"
        )

        label = (
            f"{icon} {title} · {severity} · "
            f"{detected_at} · ID {alert_id}"
        )

        with st.expander(
            label,
            expanded=(
                st.session_state.get("focus_alert")
                == alert_id
            ),
        ):

            st.write(
                "**What happened:**",
                explanation,
            )

            st.write(
                "**Suggested next step:**",
                recommendation,
            )

            st.caption(
                "Failed sign-in attempts "
                f"(if applicable): {attempts}"
            )

            if review_id in reviewed_ids:

                st.success(
                    "This warning has been reviewed."
                )

            elif st.button(
                "Mark as Reviewed",
                key=f"review_{alert_id}",
            ):

                save_review(
                    review_id,
                    title,
                )

                st.rerun()

            if st.button(
                "Create response plan",
                key=f"plan_alert_{alert_id}",
            ):

                st.session_state[
                    "plan_alert_id"
                ] = alert_id

                navigate("Response Plans")

    st.session_state.pop(
        "focus_alert",
        None,
    )


# ============================================================
# SECURITY CHECKER
# ============================================================

elif page == "Security Checker":

    st.title("🛡️ Security Checker")

    st.caption(
        "Enter sample sign-in data to test "
        "the demonstration detection rule."
    )

    with st.form("checker_form"):

        failed = st.number_input(
            "Number of failed sign-in attempts",
            min_value=0,
            max_value=100000,
            value=0,
            step=1,
        )

        run_check = st.form_submit_button(
            "Analyze Sample Activity",
            type="primary",
        )

    if run_check:

        warning = check_failed_logins(
            int(failed)
        )

        if warning:

            alert_id = save_detected_alert(
                warning
            )

            st.error(
                f"{warning['severity']} Priority: "
                f"{warning['title']}"
            )

            st.write(
                warning["explanation"]
            )

            st.write(
                "**Recommended action:**",
                warning["recommendation"],
            )

            st.success(
                "Saved demonstration warning "
                f"#{alert_id} to the database."
            )

        else:

            st.info(
                "This sample did not meet the "
                "detection rule (5 or more failed "
                "sign-ins). That does not guarantee "
                "an account is safe."
            )

    st.caption(
        "This tool does not read real sign-in "
        "logs or monitor live accounts."
    )


# ============================================================
# PROTECTION TIPS
# ============================================================

elif page == "Protection Tips":

    st.title("💡 Protection Tips")

    st.caption(
        "Practical, general steps for small businesses"
    )

    tips = [
        (
            "🔐 Use multi-factor authentication",
            "Add a second verification step "
            "to important accounts.",
        ),
        (
            "🔑 Use unique passwords",
            "Choose long, unique passwords "
            "and store them in a reputable "
            "password manager.",
        ),
        (
            "💻 Keep software updated",
            "Apply security updates "
            "from official vendors.",
        ),
        (
            "🧑‍💼 Review employee access",
            "Remove accounts that are no longer "
            "needed and limit unnecessary permissions.",
        ),
        (
            "💾 Maintain backups",
            "Keep protected backups and periodically "
            "test restoring them.",
        ),
        (
            "🎣 Watch for phishing",
            "Verify unexpected requests for "
            "passwords, payments, or sensitive "
            "information.",
        ),
    ]

    for title, description in tips:

        with st.container(border=True):
            st.subheader(title)
            st.write(description)


# ============================================================
# ACTION HISTORY
# ============================================================

elif page == "Action History":

    st.title("📋 Action History")

    st.caption(
        "A record of review actions saved "
        "in SQLite. Review does not mean remediation."
    )

    st.metric(
        "Simulated Response Plans",
        len(get_response_actions()),
    )

    if reviews:

        history = pd.DataFrame(
            reviews,
            columns=[
                "Alert ID",
                "Alert Name",
                "Reviewed At",
            ],
        )

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True,
        )

        st.metric(
            "Total Saved Reviews",
            len(reviews),
        )

    else:

        st.info(
            "No review actions have been saved yet."
        )


# ============================================================
# RESPONSE PLANS
# ============================================================

elif page == "Response Plans":

    st.title("📝 Simulated Response Plans")

    st.caption(
        "Plan and track recommended steps. "
        "These controls do NOT change passwords, "
        "block IPs, or affect real devices."
    )

    if not alerts:

        st.info(
            "Create a warning before adding "
            "a response plan."
        )

    else:

        labels = {
            alert[0]: (
                f"#{alert[0]} · {alert[1]} "
                f"({alert[2]})"
            )
            for alert in alerts
        }

        with st.form(
            "add_response_plan",
            clear_on_submit=True,
        ):

            selected = st.selectbox(
                "Choose warning",
                list(labels),
                format_func=lambda i: labels[i],
                index=(
                    list(labels).index(
                        st.session_state.get(
                            "plan_alert_id"
                        )
                    )
                    if st.session_state.get(
                        "plan_alert_id"
                    ) in labels
                    else 0
                ),
            )

            action = st.selectbox(
                "Suggested action",
                [
                    "Verify suspicious activity "
                    "with account owner",
                    "Reset password (planned only)",
                    "Enable multi-factor authentication "
                    "(planned only)",
                    "Apply software update (planned only)",
                    "Review account permissions",
                    "Investigate suspicious source IP",
                    "Document follow-up",
                ],
            )

            notes = st.text_area(
                "Notes (optional)"
            )

            if st.form_submit_button(
                "Save Response Plan",
                type="primary",
            ):

                add_response_action(
                    selected,
                    action,
                    notes,
                )

                st.success(
                    "Response plan saved. "
                    "No real security action was performed."
                )

        st.subheader(
            "Saved response plans"
        )

        for (
            ident,
            alert_id,
            action,
            status,
            notes,
            updated,
        ) in get_response_actions():

            with st.expander(
                f"#{ident} · Alert #{alert_id} · "
                f"{action} · {status}"
            ):

                with st.form(
                    f"update_plan_{ident}"
                ):

                    statuses = [
                        "Planned",
                        "In Progress",
                        "Completed",
                    ]

                    new_status = st.selectbox(
                        "Progress",
                        statuses,
                        index=statuses.index(status),
                    )

                    new_notes = st.text_area(
                        "Progress notes",
                        value=notes,
                        key=f"notes_{ident}",
                    )

                    if st.form_submit_button(
                        "Save Progress"
                    ):

                        update_response_action(
                            ident,
                            new_status,
                            new_notes,
                        )

                        st.success(
                            "Simulated plan updated."
                        )

                        st.rerun()

                st.caption(
                    f"Last updated: {updated}"
                )


# ============================================================
# TEST DATA
# ============================================================

elif page == "Test Data":

    st.title(
        "🗄️ Synthetic Security Event Database"
    )

    st.caption(
        "Events are generated locally, stored "
        "in SQLite, and are not connected "
        "to real accounts or devices."
    )

    events = get_security_events(
        limit=1000
    )

    st.metric(
        "Stored Test Events",
        len(events),
    )

    if events:

        frame = pd.DataFrame(
            events,
            columns=[
                "ID",
                "Time",
                "Event Type",
                "Account",
                "Source IP",
                "Outcome",
                "Details",
            ],
        )

        st.dataframe(
            frame,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download synthetic events CSV",
            frame.to_csv(
                index=False
            ).encode("utf-8"),
            "synthetic_security_events.csv",
            "text/csv",
        )

    st.subheader(
        "Run rule-based detection on the database"
    )

    st.write(
        "Checks failed logins (5+ per account), "
        "failures across multiple accounts "
        "from one IP, pending software updates, "
        "and newly created accounts. "
        "Duplicate findings are suppressed."
    )

    if st.button(
        "Analyze Stored Events",
        type="primary",
    ):

        created = analyze_database_events()

        if created:

            for (
                ident,
                title,
                severity,
            ) in created:

                st.success(
                    f"Saved warning #{ident}: "
                    f"{title} ({severity})."
                )

        else:

            st.info(
                "No new qualifying warnings. "
                "Previously detected patterns "
                "will not create duplicates today."
            )

    st.caption(
        "Only demo records are analyzed. "
        "No live systems are accessed."
    )


# ============================================================
# ASK ASSISTANT
# ============================================================

elif page == "Ask Assistant":

    st.title(
        "💬 Ask Assistant"
    )

    st.caption(
        "Real AI-generated explanations grounded "
        "in synthetic database records. "
        "Requires an OpenAI API key "
        "with available credits."
    )

    render_assistant_panel()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Security Assistant · "
    "Capstone demonstration · "
    "Synthetic SQLite events · "
    "OpenAI API integration · "
    "No live monitoring"
)
