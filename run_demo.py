#!/usr/bin/env python3
"""
Demo Script for Automated IT Incident Response System

This script demonstrates the full workflow of the IT Incident Response System
using both the Google Agent-to-Agent (A2A) Protocol and Anthropic's Model
Context Protocol (MCP).
"""

import os
import sys
import time
import logging
import argparse
import colorlog
from typing import Dict, Any, List

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from it_incident_response.system import IncidentResponseSystem

def setup_logging(debug: bool = False):
    """Set up colorized logging"""
    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    if debug:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)

def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def print_json(data: Dict[str, Any], indent: int = 2):
    """Pretty print JSON data"""
    import json
    print(json.dumps(data, indent=indent))

def print_incident_summary(incident: Dict[str, Any]):
    """Print a summary of an incident"""
    if not incident:
        print("No incident data available.")
        return

    print(f"Incident ID: {incident.get('incident_id')}")
    print(f"Title: {incident.get('title')}")
    print(f"Status: {incident.get('status', 'unknown')}")
    print(f"Severity: {incident.get('severity', 'unknown')}")
    print(f"Affected Systems: {', '.join(incident.get('affected_systems', []))}")
    print(f"Reported: {incident.get('reported_time')}")

    if incident.get('notes'):
        print("\nNotes:")
        for note in incident.get('notes', []):
            print(f"- {note.get('content')} ({note.get('timestamp')})")

def print_diagnostic_summary(report: Dict[str, Any]):
    """Print a summary of a diagnostic report"""
    if not report:
        print("No diagnostic report available.")
        return

    print(f"Report ID: {report.get('report_id')}")
    print(f"Status: {report.get('status', 'unknown')}")
    print(f"Root Cause: {report.get('root_cause', 'unknown')}")
    print(f"Confidence: {report.get('confidence', 0):.2f}")

    if report.get('evidence'):
        print("\nEvidence:")
        for evidence in report.get('evidence', []):
            print(f"- {evidence}")

    if report.get('recommended_actions'):
        print("\nRecommended Actions:")
        for action in report.get('recommended_actions', []):
            print(f"- {action}")

def print_resolution_summary(resolution: Dict[str, Any]):
    """Print a summary of a resolution status"""
    if not resolution:
        print("No resolution data available.")
        return

    print(f"Incident ID: {resolution.get('incident_id')}")
    print(f"Status: {resolution.get('status', 'unknown')}")
    print(f"Resolution Time: {resolution.get('resolution_time')}")

    if resolution.get('actions_taken'):
        print("\nActions Taken:")
        for action in resolution.get('actions_taken', []):
            print(f"- {action}")

    if resolution.get('verification'):
        verification = resolution.get('verification', {})
        print(f"\nVerification Status: {verification.get('status', 'unknown')}")
        if verification.get('tests_performed'):
            print("Tests Performed:")
            for test in verification.get('tests_performed', []):
                print(f"- {test}")

def wait_with_progress(seconds: int, message: str = "Processing"):
    """Display a progress indicator while waiting"""
    from tqdm import tqdm
    with tqdm(total=seconds, desc=message, unit="s") as pbar:
        for _ in range(seconds):
            time.sleep(1)
            pbar.update(1)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run the IT Incident Response System demo')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--incident-id', type=str, help='Use a specific incident ID instead of creating a new one')
    parser.add_argument('--use-preloaded', action='store_true', help='Use a preloaded incident instead of creating a new one')
    parser.add_argument('--no-analysis', action='store_true', help='Skip the analysis step')
    parser.add_argument('--no-resolution', action='store_true', help='Skip the resolution step')
    return parser.parse_args()

def run_demo():
    """Run the full demonstration"""
    args = parse_args()
    setup_logging(args.debug)

    print_section("Initializing IT Incident Response System")
    system = IncidentResponseSystem(preload_incidents=True)

    # Use existing or create new incident
    incident_id = None
    if args.incident_id:
        incident_id = args.incident_id
        print(f"Using specified incident ID: {incident_id}")
    elif args.use_preloaded:
        incidents = system.list_incidents()
        if incidents:
            incident_id = incidents[0].get('incident_id')
            print(f"Using preloaded incident ID: {incident_id}")

    if not incident_id:
        print_section("Creating New Incident")
        incident_id = system.create_incident(
            title="Database connectivity issues in production",
            description="Users reporting slow response times and intermittent errors when accessing customer data",
            severity="high",
            affected_systems=["app-server-01", "db-server-02"],
            tags=["database", "connectivity", "timeout"]
        )
        print(f"Incident created with ID: {incident_id}")

    # Get and display the incident
    incident = system.get_incident_status(incident_id)
    print_section("Incident Details")
    print_incident_summary(incident)

    if not args.no_analysis:
        print_section("Analyzing Incident")
        print("Sending incident to Diagnostic Agent for analysis...")
        wait_with_progress(5, "Analyzing incident")

        diagnostic_report = system.analyze_incident(incident_id)
        print_section("Diagnostic Report")
        print_diagnostic_summary(diagnostic_report)

        # Update incident status to identified
        print_section("Updating Incident Status")
        print("Updating incident status to 'identified'...")
        updated_incident = system.update_incident_status(
            incident_id=incident_id,
            status="identified",
            notes=f"Root cause identified: {diagnostic_report.get('root_cause')}"
        )
        print("Incident status updated.")

        # Update to resolving
        print("Updating incident status to 'resolving'...")
        system.update_incident_status(
            incident_id=incident_id,
            status="resolving"
        )
        print("Incident status updated.")

        if not args.no_resolution:
            print_section("Implementing Resolution")
            print("Sending incident to Resolution Agent for implementation...")
            wait_with_progress(8, "Implementing resolution")

            resolution_status = system.implement_resolution(incident_id)
            print_section("Resolution Status")
            print_resolution_summary(resolution_status)

    # Get final incident status
    print_section("Final Incident Status")
    final_status = system.get_incident_status(incident_id)
    print_incident_summary(final_status)

    print_section("Demo Completed")
    system.cleanup()

if __name__ == "__main__":
    run_demo()