AI Security Assistant
A Windows-friendly Streamlit cybersecurity demonstration designed to help small business owners understand potential security concerns. The application includes a dashboard, explainable detection rules, synthetic SQLite security events, review history, simulated response plans, and an optional OpenAI-powered assistant.
Educational prototype: This application uses simulated security data. It does not monitor real networks, access employee accounts, or automatically resolve threats.

1. Download the project from GitHub
1. Open this project's GitHub repository.
2. Select the green Code button, then Download ZIP.
3. Extract the ZIP to a folder on your computer.
4. Open Visual Studio Code (VS Code).
5. Select File → Open Folder and choose the extracted project folder (the folder containing app.py and requirements.txt).
6. Select Terminal → New Terminal in VS Code.
Alternative for Git users: Clone the repository using its GitHub URL, then open the cloned folder in VS Code:
git clone <YOUR-REPOSITORY-URL>
Replace <YOUR-REPOSITORY-URL> with the HTTPS URL shown under GitHub's Code button. Open the cloned project folder before continuing.
2. Install the prerequisites
You will need:
- Windows 10 or 11
- Python 3.13 with the Python launcher (py) installed: https://www.python.org/downloads/
- VS Code: https://code.visualstudio.com/
- An internet connection to install packages (and to use the optional AI Assistant)
Check Python in the VS Code terminal:
py -3.13 --version
If this command fails, install Python 3.13 and restart VS Code. Python 3.13 is the version used in the instructions below; other versions have not been verified for this project.
3. Create the virtual environment and install dependencies
Run these commands one at a time in the VS Code terminal, from the project folder:
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
The second command may take a few minutes. You do not need to activate the virtual environment manually.
4. Configure the OpenAI Assistant (optional)
The dashboard's local demonstration features can be used without an OpenAI API key if the app handles a missing key as described. To use Ask Assistant, you need an OpenAI API key with available API billing/credits.
1. In VS Code, locate .streamlit/secrets.toml.example.
2. Copy it into the same folder and rename the copy secrets.toml.
3. Edit .streamlit/secrets.toml and set your key, for example:
OPENAI_API_KEY = "paste-your-own-api-key-here"
4. Save the file. Never upload secrets.toml or your real API key to GitHub.
Create an API key: https://platform.openai.com/api-keys

Check API billing: https://platform.openai.com/settings/organization/billing/overview

A ChatGPT subscription does not include OpenAI API usage. API calls can incur charges. If you do not have an API key, skip this step and avoid using Ask Assistant. If the app displays a missing-key error at startup rather than only on the AI page, an API key may be required by this version of the application.
5. Launch the dashboard
In the VS Code terminal, run:
.\.venv\Scripts\python.exe -m streamlit run app.py
Streamlit should display a Local URL, typically:

http://localhost:8501

Open that address in your web browser if it does not open automatically. Keep the VS Code terminal open while using the dashboard. To stop the application, return to the terminal and press Ctrl+C.

To start the dashboard again later, open the project folder in VS Code and repeat only the launch command above. You do not need to reinstall dependencies every time.
6. Explore the application
1. Home: Review alert priority cards, security trends, and recent warnings.
2. Security Alerts: Browse and filter warnings; mark an alert as reviewed.
3. Security Checker: Enter a sample failed-login count to see a plain-language warning and suggested action.
4. Protection Tips: Read everyday cybersecurity recommendations.
5. Response Plans: Record recommended actions and update their statuses. These are tracking records only; the application does not execute security changes.
6. Test Data: Inspect synthetic SQLite events and select Analyze Stored Events. Demonstration detection includes five or more failed sign-ins for one account, eight or more failed sign-ins across at least two accounts from one IP, pending software updates, and newly created accounts.
7. Action History: View saved alert-review activity.
8. Ask Assistant: With an API key configured, try: Which synthetic warning is most serious, and what should the business owner do first?
The order and exact names of controls may vary slightly with the version of the project you downloaded.
7. Run automated tests (optional)
From the project folder:
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
Troubleshooting
Problem	What to try
py is not recognized or Python 3.13 cannot be found	Install Python 3.13, then reopen VS Code.
requirements.txt cannot be found	In VS Code, open the folder containing app.py and requirements.txt, then open a new terminal.
No module named streamlit	Repeat the dependency-install command in Step 3, then launch using the .venv Python command in Step 5.
PowerShell blocks script activation	Activation is not required; use the .venv\Scripts\python.exe commands above.
Browser does not open automatically	Visit http://localhost:8501 or use the Local URL shown in the terminal.
Port 8501 is already in use	Stop the other Streamlit session or open the different Local URL Streamlit provides.
Ask Assistant reports an API error	Check your key in .streamlit/secrets.toml, internet access, and API credits/billing.
The dashboard fails at startup	Read the terminal error message and verify all required project files are present.


Project files
- app.py — Streamlit dashboard, navigation, and response plans.
- database.py — SQLite tables and saved records.
- demo_data.py — synthetic demonstration events.
- event_detection.py — explainable detection rules.
- securitychecker.py — manual failed-login scenario checker.
- ai_assistant.py — OpenAI integration and read-only synthetic context.
- requirements.txt — Python dependencies.
- .streamlit/secrets.toml.example — safe configuration template; never put a real key here.
- tests/ — automated tests.
Note: These filenames reflect the documented project structure. Confirm that every file listed here is included in the GitHub repository before sharing it.
Important limitations and privacy
- Events are synthetic and are seeded on first launch. The application does not monitor live networks or access real systems.
- Detection rules are simplified demonstrations, not validated intrusion detection. A warning is not proof of an attack.
- The AI Assistant uses OpenAI API model gpt-4o-mini and may incur usage charges.
- The application sends a limited, read-only summary of synthetic alerts, events, and response plans to the AI provider when AI features are used. Do not enter real credentials or sensitive business information.
- Marking an alert reviewed or completing a response plan records user activity; it does not prove a threat has been resolved.
- This is an educational prototype, not a production security system.
Existing project database (optional)
For users migrating from a previous copy of the project: back up the original folder and security_assistant.db before copying anything. The application creates missing tables using CREATE TABLE IF NOT EXISTS, and sample events are seeded when their table is empty. Only copy an older database if you understand its compatibility with this version.
GitHub and credential safety
The .gitignore should exclude .streamlit/secrets.toml, .env, .venv/, SQLite databases, and temporary files. Check the repository contents before publishing. Never commit an OpenAI API key. If a real key was previously committed, revoke it and create a new one.
Dashboard layout
The Home page includes dark navigation, a blue header, four priority cards, recent alert rows, an AI panel, a security trend, affected areas, and quick actions. Displayed figures are calculated from synthetic SQLite records rather than copied from a static screenshot.

## OpenAI API billing

This edition uses `gpt-4o-mini` via the OpenAI API. ChatGPT Free/Plus/Pro subscriptions do **not** provide free API calls. If your API balance is exhausted, the AI panel will report an API error; all local dashboard and SQLite features still work. Create a key at https://platform.openai.com/api-keys and review billing at https://platform.openai.com/settings/organization/billing/overview. Never commit `.streamlit/secrets.toml`.


## Reference dashboard layout
The Home page has been redesigned to closely match the supplied screenshot: dark navy navigation, blue header, four colored priority cards, colored recent alert rows, right-side AI panel, security trend, affected areas, and quick actions. Figures are calculated from your actual synthetic SQLite records rather than hard-coded to the screenshot. The AI conversation stays on Ask Assistant to prevent horizontal overflow.
