#!/usr/bin/env python3
"""
Example script demonstrating how to use the AI PR Review API programmatically
"""

import requests
import json


# API base URL (change if running on a different host/port)
API_BASE = 'http://localhost:5000'


def check_health():
    """Check if the API is running"""
    try:
        response = requests.get(f'{API_BASE}/api/health')
        data = response.json()
        print("API Health Check:")
        print(f"  Status: {data['status']}")
        print(f"  GitHub configured: {data['github_configured']}")
        print(f"  Claude configured: {data['claude_configured']}")
        return data['status'] == 'healthy'
    except Exception as e:
        print(f"Error: {e}")
        return False


def review_pr(pr_url: str):
    """Review a PR and print the results"""
    print(f"\nReviewing PR: {pr_url}")
    print("-" * 50)

    try:
        response = requests.post(
            f'{API_BASE}/api/review',
            json={'pr_url': pr_url}
        )

        data = response.json()

        if 'error' in data:
            print(f"Error: {data['error']}")
            return None

        # Print PR info
        pr_info = data.get('pr_info', {})
        print(f"\nPR #{pr_info.get('number')}: {pr_info.get('title')}")
        print(f"Author: {pr_info.get('author')}")
        print(f"Branch: {pr_info.get('head_branch')} -> {pr_info.get('base_branch')}")

        # Print statistics
        stats = data.get('statistics', {})
        print(f"\nStatistics:")
        print(f"  Files changed: {stats.get('total_files')}")
        print(f"  Additions: +{stats.get('total_additions')}")
        print(f"  Deletions: -{stats.get('total_deletions')}")

        # Print analysis
        analysis = data.get('analysis', {})
        print(f"\nRisk Level: {analysis.get('risk_level', 'unknown').upper()}")
        print(f"\nSummary:")
        print(f"  {analysis.get('summary', 'N/A')}")

        # Print issues
        issues = analysis.get('issues', [])
        if issues:
            print(f"\nIssues Found ({len(issues)}):")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. [{issue.get('severity', 'info').upper()}] {issue.get('description')}")
                if issue.get('file'):
                    print(f"     File: {issue.get('file')}")
                if issue.get('suggestion'):
                    print(f"     Suggestion: {issue.get('suggestion')}")

        # Print suggestions
        suggestions = analysis.get('suggestions', [])
        if suggestions:
            print(f"\nSuggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")

        return data

    except Exception as e:
        print(f"Error: {e}")
        return None


def analyze_file(pr_url: str, filename: str):
    """Perform deep analysis on a specific file"""
    print(f"\nAnalyzing file: {filename}")
    print("-" * 50)

    try:
        response = requests.post(
            f'{API_BASE}/api/analyze-file',
            json={
                'pr_url': pr_url,
                'filename': filename
            }
        )

        data = response.json()

        if 'error' in data:
            print(f"Error: {data['error']}")
            return None

        print(f"\nAnalysis:")
        print(data.get('analysis', 'N/A'))

        return data

    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    """Main function"""
    print("AI PR Review - Example Usage")
    print("=" * 50)

    # Check API health
    if not check_health():
        print("\nAPI is not running. Please start the server first:")
        print("  python app.py")
        return

    # Example PR URL (replace with an actual PR)
    example_pr = "https://github.com/anthropics/anthropic-sdk-python/pull/100"

    print(f"\nExample PR: {example_pr}")
    print("Note: Replace with an actual PR URL to test")

    # Ask user for PR URL
    pr_url = input("\nEnter PR URL (or press Enter to use example): ").strip()
    if not pr_url:
        pr_url = example_pr

    # Review the PR
    result = review_pr(pr_url)

    if result:
        # Optionally analyze a specific file
        files = result.get('files_changed', [])
        if files:
            print("\n" + "=" * 50)
            print("Files changed:")
            for i, f in enumerate(files[:10], 1):
                print(f"  {i}. {f.get('filename')}")

            file_choice = input("\nEnter file number for deep analysis (or press Enter to skip): ").strip()
            if file_choice and file_choice.isdigit():
                idx = int(file_choice) - 1
                if 0 <= idx < len(files):
                    analyze_file(pr_url, files[idx].get('filename'))


if __name__ == '__main__':
    main()
