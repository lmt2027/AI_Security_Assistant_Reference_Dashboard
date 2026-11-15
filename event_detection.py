"""Explainable, idempotent detection rules for SYNTHETIC database events."""
from collections import defaultdict
from datetime import datetime, timedelta
from database import get_security_events, save_detected_alert, record_detection_key


def analyze_database_events(now=None):
    now = now or datetime.now()
    cutoff = now - timedelta(hours=24)
    events = []
    for e in get_security_events(limit=2000):
        try:
            timestamp = datetime.fromisoformat(e[1])
        except (TypeError, ValueError):
            continue
        if cutoff <= timestamp <= now:
            events.append(e)

    candidates = []
    failed_by_account = defaultdict(list)
    failed_by_ip = defaultdict(list)
    for e in events:
        _, _, kind, account, ip, outcome, details = e
        if kind == 'login' and outcome == 'failure':
            failed_by_account[account].append(e)
            failed_by_ip[ip].append(e)
        if kind == 'software_update' and outcome == 'pending':
            candidates.append((f'pending-update:{e[0]}', {
                'title': 'Software Update Pending', 'severity': 'Medium',
                'explanation': f'Sample software update event #{e[0]} is marked pending.',
                'recommendation': 'Verify the software and apply an approved vendor update.',
                'failed_attempts': 0,
            }))
        if kind == 'account_created' and outcome == 'success':
            candidates.append((f'new-account:{e[0]}', {
                'title': 'New Account Requires Review', 'severity': 'Low',
                'explanation': f'Sample account creation event #{e[0]} should be checked for authorization.',
                'recommendation': 'Confirm the account was requested and has appropriate access.',
                'failed_attempts': 0,
            }))
    for account, failures in failed_by_account.items():
        if len(failures) >= 5:
            n = len(failures)
            candidates.append((f'failed-login:{account}:{now.date().isoformat()}', {
                'title': 'Possible Password Attack', 'severity': 'High' if n >= 8 else 'Medium',
                'explanation': f'The synthetic event database contains {n} failed sign-ins for {account} in the last 24 hours.',
                'recommendation': 'Confirm activity with the account owner, review access, and enable multi-factor authentication.',
                'failed_attempts': n,
            }))
    for ip, failures in failed_by_ip.items():
        accounts = {e[3] for e in failures}
        if len(failures) >= 8 and len(accounts) >= 2:
            candidates.append((f'multi-account-ip:{ip}:{now.date().isoformat()}', {
                'title': 'Multiple Accounts Targeted From One Source', 'severity': 'High',
                'explanation': f'Sample IP {ip} has {len(failures)} failed logins across {len(accounts)} accounts in 24 hours.',
                'recommendation': 'Investigate the source, review affected accounts and consider appropriate access restrictions.',
                'failed_attempts': len(failures),
            }))
    created = []
    for key, alert in candidates:
        if not record_detection_key(key):
            continue
        ident = save_detected_alert(alert)
        created.append((ident, alert['title'], alert['severity']))
    return created
