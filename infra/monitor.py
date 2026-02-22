#!/usr/bin/env python3
"""
AI API Usage Monitor
Usage:
  python3 monitor.py check    # Check once, output table
  python3 monitor.py watch    # Watch mode: loop every 300s
  python3 monitor.py history  # Show last 24h history
"""

import sqlite3
import json
import os
import sys
import time
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# Database path
DB_PATH = os.path.expanduser('~/Downloads/dispatch/dispatch/monitor.db')


def get_api_key(provider):
    """
    Get API key from:
    1. Environment variable: <PROVIDER>_API_KEY or ZAI_API_KEY (for GLM)
    2. File: ~/.oyster-keys/<provider> or ~/.oyster-keys/<provider>.env
    3. Return None if not found
    """
    # Special handling for GLM - check ZAI_API_KEY
    if provider.lower() == 'glm':
        api_key = os.environ.get('ZAI_API_KEY')
        if api_key:
            return api_key

    # Check environment variable first
    env_key = f"{provider.upper()}_API_KEY"
    api_key = os.environ.get(env_key)
    if api_key:
        return api_key

    # Check file in ~/.oyster-keys/<provider> or ~/.oyster-keys/<provider>.env
    key_files = [
        os.path.expanduser(f"~/.oyster-keys/{provider.lower()}"),
        os.path.expanduser(f"~/.oyster-keys/{provider.lower()}.env")
    ]

    # For GLM, also check zai-glm.env
    if provider.lower() == 'glm':
        key_files.append(os.path.expanduser("~/.oyster-keys/zai-glm.env"))

    for key_file in key_files:
        try:
            with open(key_file, 'r') as f:
                content = f.read()
                # Try to parse as .env format (export KEY="value")
                if 'export ' in content and '=' in content:
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.startswith('export ') and '=' in line:
                            # Remove "export " and parse key=value
                            kv = line[7:].strip()
                            if '=' in kv:
                                key, value = kv.split('=', 1)
                                key = key.strip()
                                value = value.strip()
                                # Remove quotes
                                if value.startswith('"') and value.endswith('"'):
                                    value = value[1:-1]
                                elif value.startswith("'") and value.endswith("'"):
                                    value = value[1:-1]
                                # Check if this is the key we want
                                if provider.lower() == 'glm' and key in ('ZAI_API_KEY', 'GLM_API_KEY'):
                                    return value
                                elif key.upper() == f"{provider.upper()}_API_KEY":
                                    return value
                else:
                    # Simple key file
                    key_content = content.strip()
                    if key_content:
                        return key_content
        except (FileNotFoundError, PermissionError):
            pass

    return None


def fetch_minimax_coding_plan(api_key):
    """
    Fetch MiniMax coding plan remaining quota.
    API: GET https://www.minimax.io/v1/api/openplatform/coding_plan/remains
    Auth: Bearer <coding-plan-key> (from minimax-key.txt)
    Returns list of model quotas or None.
    """
    url = "https://www.minimax.io/v1/api/openplatform/coding_plan/remains"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        req = Request(url, headers=headers)
        req.add_header('User-Agent', 'dispatch-monitor/1.0')
        req.add_header('Accept', '*/*')
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            base = data.get('base_resp', {})
            if base.get('status_code') == 0:
                models = data.get('model_remains', [])
                return models
    except (URLError, HTTPError, json.JSONDecodeError, Exception):
        pass

    return None


def check_provider(provider):
    """
    Check a provider's usage status
    Returns dict with status info
    """
    result = {
        'provider': provider,
        'status': 'error',
        'emoji': '❌',
        'used': 'N/A',
        'remaining': 'N/A',
        'currency': '',
        'message': ''
    }

    # Get API key
    api_key = get_api_key(provider)
    if not api_key:
        result.update({
            'status': 'skip',
            'emoji': '⏭️',
            'message': '(no key, skip)'
        })
        return result

    # Handle based on provider type
    if provider.lower() == 'glm':
        # Z.AI GLM Coding Plan — subscription, no balance REST API
        result.update({
            'status': 'ok',
            'emoji': '✅',
            'used': 'N/A',
            'remaining': 'N/A',
            'message': '(Z.AI Coding Plan, check z.ai/manage-apikey/billing)'
        })

    elif provider.lower() == 'minimax':
        # Read coding plan key from minimax-key.txt (different from general API key)
        cp_key_path = os.path.expanduser('~/.oyster-keys/minimax-key.txt')
        cp_key = None
        try:
            with open(cp_key_path, 'r') as f:
                cp_key = f.read().strip()
        except (FileNotFoundError, PermissionError):
            pass

        if not cp_key:
            cp_key = api_key  # fallback to general key

        models = fetch_minimax_coding_plan(cp_key)
        if models:
            # usage_count = remaining prompts (not used), total_count = max per window
            total_quota = sum(m.get('current_interval_total_count', 0) for m in models)
            total_remaining = sum(m.get('current_interval_usage_count', 0) for m in models)
            total_used = total_quota - total_remaining

            # Window time info from first model
            remains_ms = models[0].get('remains_time', 0)
            remains_min = remains_ms // 60000

            remaining_pct = (total_remaining / total_quota * 100) if total_quota > 0 else 0
            window_info = f"{remains_min}min left in window"

            result.update({
                'used': f"{total_used}/{total_quota}",
                'remaining': str(total_remaining),
                'currency': 'prompts',
                'message': f'{remaining_pct:.0f}% free | {window_info}'
            })

            if remaining_pct < 5:
                result['status'] = 'critical'
                result['emoji'] = '🚨'
            elif remaining_pct < 20:
                result['status'] = 'warning'
                result['emoji'] = '⚠️'
            else:
                result['status'] = 'ok'
                result['emoji'] = '✅'
        else:
            result.update({
                'status': 'info',
                'emoji': 'ℹ️',
                'used': 'N/A',
                'remaining': 'N/A',
                'message': '(API query failed)'
            })

    return result


def init_database(db_path):
    """Initialize monitor database schema"""
    # Ensure directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS usage_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            provider TEXT NOT NULL,
            used REAL,
            remaining REAL,
            currency TEXT DEFAULT 'USD',
            status TEXT DEFAULT 'ok'
        );
        CREATE INDEX IF NOT EXISTS idx_snap_ts ON usage_snapshots(timestamp);
        CREATE INDEX IF NOT EXISTS idx_snap_provider ON usage_snapshots(provider);
    ''')
    conn.commit()
    conn.close()


def save_snapshot(db_path, provider_info):
    """Save usage snapshot to database"""
    conn = sqlite3.connect(db_path, timeout=10.0)

    # Extract numeric values for storage
    used_val = None
    remaining_val = None

    if isinstance(provider_info['used'], (int, float)):
        used_val = provider_info['used']
    elif isinstance(provider_info['used'], str) and provider_info['used'] != 'N/A':
        # Try to extract number
        try:
            used_val = float(provider_info['used'].replace('¥', '').replace('$', '').strip())
        except ValueError:
            pass

    if isinstance(provider_info['remaining'], (int, float)):
        remaining_val = provider_info['remaining']
    elif isinstance(provider_info['remaining'], str) and provider_info['remaining'] != 'N/A':
        try:
            remaining_val = float(provider_info['remaining'].replace('¥', '').replace('$', '').strip())
        except ValueError:
            pass

    conn.execute('''
        INSERT INTO usage_snapshots (timestamp, provider, used, remaining, currency, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        provider_info['provider'],
        used_val,
        remaining_val,
        provider_info.get('currency', ''),
        provider_info['status']
    ))
    conn.commit()
    conn.close()


def print_table(providers):
    """Print usage table"""
    print("\n=== AI API Usage Monitor ===", flush=True)

    # Header
    print(f"{'Provider':<16} {'Status':<12} {'Used':<12} {'Remaining':<12} {'Alert'}", flush=True)
    print("-" * 70, flush=True)

    # Rows
    for p in providers:
        provider_name = p['provider']
        if provider_name == 'glm':
            display_name = 'GLM (智谱)'
        elif provider_name == 'minimax':
            display_name = 'MiniMax'
        else:
            display_name = provider_name

        # Format alert column
        alert_msg = p['message'] if p['message'] else ''

        print(f"{display_name:<16} {p['emoji']} {p['status']:<9} {p['used']:<12} {p['remaining']:<12} {alert_msg}", flush=True)

    print("-" * 70, flush=True)
    print(f"Last check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", flush=True)


def cmd_check():
    """Check command: check once and display"""
    # Initialize database
    init_database(DB_PATH)

    # Providers to check (only GLM and MiniMax)
    providers = ['glm', 'minimax']

    results = []
    for provider in providers:
        info = check_provider(provider)
        # Skip providers with no key
        if info['status'] != 'skip':
            results.append(info)
            # Save to database
            save_snapshot(DB_PATH, info)

    if results:
        print_table(results)
    else:
        print("\n=== AI API Usage Monitor ===")
        print("No providers with API keys found.\n")


def cmd_watch():
    """Watch command: loop every 300 seconds"""
    print("=== AI API Usage Monitor - Watch Mode ===", flush=True)
    print("Press Ctrl+C to stop\n", flush=True)

    try:
        while True:
            cmd_check()
            print("Next check in 300 seconds...\n", flush=True)
            time.sleep(300)
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)


def cmd_history():
    """History command: show last 24h history"""
    db_path = DB_PATH

    if not os.path.exists(db_path):
        print("\n=== API Usage History (Last 24h) ===")
        print("No history data found. Run 'check' first.\n")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Get providers with data
    providers = conn.execute('''
        SELECT DISTINCT provider FROM usage_snapshots
        ORDER BY provider
    ''').fetchall()

    if not providers:
        print("\n=== API Usage History (Last 24h) ===")
        print("No history data found.\n")
        conn.close()
        return

    # Get cutoff time (24h ago)
    cutoff = (datetime.now() - timedelta(hours=24)).isoformat()

    print("\n=== API Usage History (Last 24h) ===\n")

    for provider_row in providers:
        provider = provider_row['provider']

        # Display name mapping
        display_names = {
            'glm': 'GLM (智谱)',
            'minimax': 'MiniMax'
        }
        display_name = display_names.get(provider, provider)

        print(f"--- {display_name} ---")

        # Get snapshots
        snapshots = conn.execute('''
            SELECT * FROM usage_snapshots
            WHERE provider = ? AND timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (provider, cutoff)).fetchall()

        if snapshots:
            for snap in snapshots:
                ts = datetime.fromisoformat(snap['timestamp']).strftime('%Y-%m-%d %H:%M')
                used = f"{snap['used']:.2f}" if snap['used'] is not None else 'N/A'
                remaining = f"{snap['remaining']:.2f}" if snap['remaining'] is not None else 'N/A'
                currency = snap['currency'] if snap['currency'] else ''
                print(f"  [{ts}] Used: {used}{currency} | Remaining: {remaining}{currency} | Status: {snap['status']}")
        else:
            print("  No data in last 24h")

        print()

    conn.close()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'check':
        cmd_check()
    elif command == 'watch':
        cmd_watch()
    elif command == 'history':
        cmd_history()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
