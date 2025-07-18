#!/usr/bin/env python3
"""
Test script for Claude Code Web UI endpoints
"""


import requests

base_url = 'http://localhost:5000'
test_results = []

def test_endpoint(endpoint, method='GET', data=None):
    try:
        print(f'Testing {method} {endpoint}...')
        if method == 'GET':
            response = requests.get(f'{base_url}{endpoint}', timeout=5)
        elif method == 'POST':
            response = requests.post(f'{base_url}{endpoint}', json=data, timeout=5)

        if response.status_code == 200:
            print(f'✅ {endpoint} - OK')
            return True
        else:
            print(f'❌ {endpoint} - Status: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ {endpoint} - Error: {e}')
        return False

def main():
    print('Starting Claude Code Web UI endpoint tests...')

    # Test endpoints
    success_count = 0
    total_tests = 4

    if test_endpoint('/'):
        success_count += 1
    if test_endpoint('/api/system-metrics'):
        success_count += 1
    if test_endpoint('/api/tasks'):
        success_count += 1
    if test_endpoint('/api/slack-status'):
        success_count += 1

    print(f'\n✅ Web UI endpoint tests completed: {success_count}/{total_tests} passed')

    if success_count == total_tests:
        print('🎉 All tests passed! Web UI is working correctly.')
        return 0
    else:
        print('⚠️ Some tests failed. Check the Web UI server.')
        return 1

if __name__ == '__main__':
    exit(main())
