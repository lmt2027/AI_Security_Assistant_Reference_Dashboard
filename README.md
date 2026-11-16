AI Security Assistant — Setup and Demonstration Guide

Start here. This guide is for someone who has never used this project. AI Security Assistant is an educational Streamlit cybersecurity dashboard for small businesses. It uses simulated security data, not real security monitoring.

Run in GitHub Codespaces 
You need a GitHub account with Codespaces access. Codespaces runs VS Code and the app in your browser; you do not need to install Python or VS Code on your computer.

1. Open the GitHub repository link supplied with the assignment. If the repository is private, the owner must grant you access.


2. On the repository page, click the green Code button.


3. Choose the Codespaces tab, then Create codespace on main. Wait for the browser-based VS Code editor to finish opening.


4. In Codespaces, click Terminal → New Terminal at the top of the editor. Commands below go into this terminal, not into a Python file.


5. Make sure the file list on the left includes app.py and requirements.txt. Run these commands one line at a time, pressing Enter after each:
   
   python3 -m venv .venv

   .venv/bin/python -m pip install -r requirements.txt

   Installation may take several minutes. Wait until the second command finishes before proceeding.
   
6. Start the dashboard:

   .venv/bin/python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
   
7. Keep the terminal running. In the Codespaces editor, open the Ports tab (usually in the bottom panel, beside Terminal). Find port 8501, then click the globe icon or Open in Browser. If prompted to make the port available, use the Codespaces port controls. Do not expose a public port if you plan to enter private data.


8. The AI Security Assistant dashboard should open in a new browser tab. If it does not, see Troubleshooting below.


9. To stop the app, return to the terminal and press Ctrl+C. To start it again in the same Codespace, repeat only step 6.


Optional: Enable Ask Assistant
The dashboard's local features should work without an OpenAI API key if the application handles missing credentials as described. The Ask Assistant feature requires a separate OpenAI API key with active API billing; a ChatGPT subscription does not include API credits.

For Codespaces, use a Codespaces secret rather than committing a real key to the repository. In GitHub, open Settings → Codespaces → Secrets → New secret, name it OPENAI_API_KEY, enter your key, and grant access to the repository. Restart the Codespace if needed. Whether the app reads this environment variable depends on the version of ai_assistant.py included in the repository. Alternatively, if the app supports Streamlit secrets, create .streamlit/secrets.toml inside your own Codespace with:
OPENAI_API_KEY = "your-key-here"
Never commit, publish, or screenshot a real API key. The repository's .gitignore should exclude .streamlit/secrets.toml.


Demonstration: what to click and what to expect
The dashboard uses synthetic/sample security events. Exact counts may differ by run or database state.
1. Home: View the overview, high/medium/low-priority alert cards, recent warnings, trend, and navigation links.
2. Test Data: Review the sample records. Click Analyze Stored Events to evaluate them. The detection examples described for this project include five or more failed sign-ins for one account, eight or more failed sign-ins across at least two accounts from one IP address, pending software updates, and newly created accounts. Repeating the analysis should avoid creating duplicate alerts for the same already-detected patterns.
3. Security Alerts: Open an alert, read its plain-language explanation and recommendation, try the filters, and click Mark as Reviewed on an appropriate warning.
4. Action History: Confirm that the reviewed alert appears in the history.
5. Security Checker: Enter 3 failed login attempts and run the check (expected: no warning). Then enter 10 and run it again (expected: a high-priority possible password attack warning and recommended next steps).
6. Protection Tips: Read the suggested everyday security practices.
7. Response Plans: View recommendations; if controls are available, add a simulated response action and change its status. These actions are records only and do not change any real account or network.
8. Ask Assistant (optional): If an OpenAI API key is configured, ask: “Which synthetic warning is most serious, and what should the business owner do first?” Wait for the response. Without a key, skip this step.
Success check: The Home page loads; sample data is visible; the checker shows different results for 3 and 10 attempts; alerts can be reviewed and appear in history; and the app remains usable as you move between pages. AI responses are optional and depend on an API key and network/billing availability.

Troubleshooting

Issue	What to do
No Codespaces tab or permission error	Ask the repository owner for access and confirm Codespaces is enabled, or use Option B.
app.py or requirements.txt not found	Open the correct project folder/repository root.
python3 or py not found	Install a compatible Python version or check the Python executable available in your environment.
No module named streamlit	Repeat the dependency installation command for your operating system.
requirements.txt installation fails	Copy the full terminal error and check Python/package compatibility; do not assume installation succeeded.
Browser page does not open in Codespaces	Check the Ports tab for port 8501 and select Open in Browser.
Browser page does not open locally	Try http://localhost:8501 or the Local URL printed by Streamlit.
Port 8501 is already in use	Stop an existing Streamlit process or open the alternate URL/port shown by Streamlit.
AI Assistant returns an error	Verify the API key, API credits, internet access, and that the app can read the key. Other features can be demonstrated without AI.
Database-related error	Read the app's warning and preserve the existing .db file before attempting any reset or migration.


Project files (expected in the repository)
- app.py — Streamlit dashboard and navigation
- database.py — SQLite storage
- demo_data.py — synthetic sample data
- event_detection.py — detection rules
- securitychecker.py — manual failed-login checker
- ai_assistant.py — OpenAI integration
- requirements.txt — dependencies
- .streamlit/secrets.toml.example — optional safe configuration template
- tests/ — automated tests
These filenames reflect the documented project structure. If any file is missing from the actual GitHub repository, the owner must upload it or adjust these instructions before handing the project to the TA.
Run automated tests (optional)
In Codespaces or on Mac:
.venv/bin/python -m unittest discover -s tests -v
On Windows:
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
Limitations and safety
This is an educational prototype, not a production cybersecurity service. It uses synthetic data and does not monitor real networks, execute remediation, or establish that a threat has been resolved. Review and response statuses are tracking records only. Do not enter real credentials or sensitive business information. OpenAI requests send a limited summary of synthetic security information to an external AI provider and may incur charges.
