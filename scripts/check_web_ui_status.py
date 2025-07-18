#!/usr/bin/env python3
"""
Check Claude Code Web UI status
"""


import requests


def main():
    print('📊 Claude Code Web UI Status Check...')

    try:
        response = requests.get('http://localhost:5000/api/system-metrics', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print('✅ Claude Code Web UI is running')
            print('📊 System Status:')
            print(f'  Memory: {data["system"]["memory"]["percent"]:.1f}%')
            print(f'  CPU: {data["system"]["cpu"]["percent"]:.1f}%')
            print(f'  Disk: {data["system"]["disk"]["percent"]:.1f}%')
            if 'tasks' in data:
                print(f'  Tasks: {data["tasks"]}')

            # Check Slack status
            try:
                slack_response = requests.get('http://localhost:5000/api/slack-status', timeout=5)
                if slack_response.status_code == 200:
                    slack_data = slack_response.json()
                    if slack_data.get('connected'):
                        print(f'  Slack: ✅ Connected ({slack_data.get("team", "Unknown")})')
                    else:
                        print('  Slack: ❌ Not connected')
                else:
                    print('  Slack: ❌ Status check failed')
            except Exception as e:
                print(f'  Slack: ❌ Error checking status: {e}')

            return 0
        else:
            print(f'❌ Web UI not responding (Status: {response.status_code})')
            return 1
    except Exception as e:
        print(f'❌ Web UI not accessible: {e}')
        print('💡 Start the server with: make claude-code-web-ui')
        return 1

if __name__ == '__main__':
    exit(main())
