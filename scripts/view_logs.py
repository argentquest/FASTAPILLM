#!/usr/bin/env python3
"""
Simple script to view and tail log files in a readable format
"""
import json
import sys
import time
from pathlib import Path
from datetime import datetime
import argparse

def format_log_entry(line):
    """Format a JSON log entry for human reading"""
    try:
        data = json.loads(line.strip())
        timestamp = data.get('timestamp', '')
        level = data.get('level', 'INFO').upper()
        logger = data.get('logger', '')
        event = data.get('event', '')
        
        # Format timestamp
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        # Build readable line
        parts = [
            f"[{timestamp}]" if timestamp else "",
            f"[{level}]",
            f"[{logger}]" if logger else "",
            event
        ]
        
        readable = " ".join(filter(None, parts))
        
        # Add additional context if available
        extras = []
        for key, value in data.items():
            if key not in ['timestamp', 'level', 'logger', 'event', 'filename', 'lineno']:
                if isinstance(value, (str, int, float)):
                    extras.append(f"{key}={value}")
        
        if extras:
            readable += f" | {', '.join(extras)}"
            
        return readable
        
    except json.JSONDecodeError:
        return line.strip()  # Return as-is if not JSON

def tail_file(filepath, follow=False):
    """Tail a file, optionally following new lines"""
    try:
        with open(filepath, 'r') as f:
            # Go to end of file if following
            if follow:
                f.seek(0, 2)
            
            # Read existing lines if not following
            if not follow:
                for line in f:
                    if line.strip():
                        print(format_log_entry(line))
            
            # Follow new lines
            if follow:
                print(f"Following {filepath}... (Press Ctrl+C to stop)")
                while True:
                    line = f.readline()
                    if line:
                        if line.strip():
                            print(format_log_entry(line))
                    else:
                        time.sleep(0.1)
                        
    except KeyboardInterrupt:
        print("\nStopped following log file")
    except FileNotFoundError:
        print(f"Error: Log file {filepath} not found")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='View application log files')
    parser.add_argument('--file', '-f', default='logs/app.log', 
                       help='Log file path (default: logs/app.log)')
    parser.add_argument('--follow', '-F', action='store_true',
                       help='Follow the log file for new entries')
    parser.add_argument('--lines', '-n', type=int, default=None,
                       help='Show only the last N lines')
    
    args = parser.parse_args()
    
    log_path = Path(args.file)
    
    if not log_path.exists():
        print(f"Error: Log file {log_path} does not exist")
        sys.exit(1)
    
    if args.lines:
        # Show last N lines
        try:
            with open(log_path, 'r') as f:
                lines = f.readlines()
                for line in lines[-args.lines:]:
                    if line.strip():
                        print(format_log_entry(line))
        except Exception as e:
            print(f"Error reading log file: {e}")
            sys.exit(1)
    else:
        # Show all or follow
        tail_file(log_path, args.follow)

if __name__ == "__main__":
    main()