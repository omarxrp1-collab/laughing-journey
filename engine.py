#!/usr/bin/env python3
"""
Simple Engine Module
A basic engine that can be started and displays running status.
"""

import time
import sys


class Engine:
    """A simple engine class that can be started and stopped."""
    
    def __init__(self, name="Engine"):
        self.name = name
        self.is_running = False
        self.start_time = None
    
    def start(self):
        """Start the engine."""
        if self.is_running:
            print(f"{self.name} is already running!")
            return
        
        print(f"Starting {self.name}...")
        self.is_running = True
        self.start_time = time.time()
        print(f"✓ {self.name} started successfully!")
        print(f"Status: Running")
    
    def stop(self):
        """Stop the engine."""
        if not self.is_running:
            print(f"{self.name} is not running!")
            return
        
        print(f"Stopping {self.name}...")
        self.is_running = False
        elapsed = time.time() - self.start_time if self.start_time else 0
        print(f"✓ {self.name} stopped after {elapsed:.2f} seconds")
    
    def status(self):
        """Get the current status of the engine."""
        if self.is_running:
            elapsed = time.time() - self.start_time if self.start_time else 0
            return f"{self.name} is running (uptime: {elapsed:.2f}s)"
        return f"{self.name} is stopped"


def main():
    """Main entry point for the engine application."""
    print("=" * 50)
    print("Engine Application")
    print("=" * 50)
    
    engine = Engine("Main Engine")
    
    # Start the engine
    engine.start()
    
    # Display status
    print(f"\n{engine.status()}")
    
    # Simulate some work
    print("\nEngine is working...")
    for i in range(3):
        time.sleep(1)
        print(f"  → Processing... {i+1}/3")
    
    print(f"\n{engine.status()}")
    
    # Stop the engine
    print()
    engine.stop()
    
    print("\n" + "=" * 50)
    print("Engine application completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
