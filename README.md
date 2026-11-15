# AI Security Assistant — Complete Capstone Prototype

A Windows-friendly Streamlit cybersecurity demonstration for small business owners. Includes an OpenAI API-powered AI assistant, SQLite synthetic test data, explainable detection rules, a polished dashboard, review history, and user-managed **simulated** response plans.

## Quick start (Windows / VS Code)

1. Extract the ZIP and open its project folder in VS Code.
2. In the terminal, run:

   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and paste your OpenAI API key in `OPENAI_API_KEY`. Keep the file private.
4. Start the app:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```
5. Visit `http://localhost:8501`.

## Demonstration workflow

1. Open **Home** to see alert priorities, trend and recent warnings.
2. Open **Test Data**, inspect generated SQLite records, and click **Analyze Stored Events**. Detection includes: 5+ failed sign-ins for one account, 8+ failed sign-ins across 2+ accounts from one IP, pending software updates, and newly created accounts.
3. Open **Security Alerts**, filter by severity, and mark a warning reviewed.
4. Open **Response Plans**, add a recommended action, and update its status. **These are tracking records only**: the app does not execute security remediation.
5. Open **Ask Assistant** and ask: *Which synthetic warning is most serious, and what should the business owner do first?*
6. Open **Action History** to view saved review activity.

## Important limitations

- All events are synthetic and seeded on the first launch. The app does **not** monitor live networks or access real systems.
- Rules are simplified demonstrations, not validated intrusion detection. A warning is not proof of an attack.
- The AI model is accessed through OpenAI API using `gpt-4o-mini`. This requires an OpenAI API key with active API billing/credits. A ChatGPT subscription does not include API usage. API requests incur charges.
- The app sends a bounded read-only summary of synthetic alerts/events/response plans to the external AI provider; never enter real credentials or sensitive business data.
- A review or completed response plan is a record of user activity, **not** proof that a threat has been resolved.
- This is an educational prototype, not a production security platform.

## Files

- `app.py` — Streamlit pages, navigation, dashboard and response plans.
- `database.py` — SQLite schema and persistence; tables created automatically.
- `demo_data.py` — reproducible synthetic sample records.
- `event_detection.py` — transparent, idempotent detection rules.
- `securitychecker.py` — manual failed-login scenario checker.
- `ai_assistant.py` — OpenAI API integration and read-only database context.
- `.streamlit/secrets.toml.example` — safe key placeholder; **do not commit real secrets**.
- `tests/` — offline automated tests.

## Run tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Existing project migration

Keep your old folder as a backup. This ZIP is a complete standalone project. If you want to preserve an existing `security_assistant.db`, copy it into the new project **after backing it up** and before first launch. Tables are added using `CREATE TABLE IF NOT EXISTS`. The sample data is only seeded when its table is empty.

## GitHub safety

`.gitignore` excludes `.streamlit/secrets.toml`, `.venv`, `.env`, SQLite databases and caches. Verify `git status` before committing. Never commit an API key.

## OpenAI API billing

This edition uses `gpt-4o-mini` via the OpenAI API. ChatGPT Free/Plus/Pro subscriptions do **not** provide free API calls. If your API balance is exhausted, the AI panel will report an API error; all local dashboard and SQLite features still work. Create a key at https://platform.openai.com/api-keys and review billing at https://platform.openai.com/settings/organization/billing/overview. Never commit `.streamlit/secrets.toml`.


## Reference dashboard layout
The Home page has been redesigned to closely match the supplied screenshot: dark navy navigation, blue header, four colored priority cards, colored recent alert rows, right-side AI panel, security trend, affected areas, and quick actions. Figures are calculated from your actual synthetic SQLite records rather than hard-coded to the screenshot. The AI conversation stays on Ask Assistant to prevent horizontal overflow.
