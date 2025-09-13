#!/usr/bin/env python3
import pyfiglet
import subprocess
import sys

def create_fancy_title():
    """Create a fancy colorful title for OSINTube"""
    try:
        # Create ASCII art with pyfiglet
        ascii_art = pyfiglet.figlet_format('OSINTube', font='big')
        
        # Try to colorize with lolcat
        try:
            result = subprocess.run(['lolcat'], input=ascii_art, text=True, capture_output=True)
            if result.returncode == 0:
                return result.stdout
        except FileNotFoundError:
            pass
        
        # Fallback to plain ASCII art
        return ascii_art
        
    except Exception:
        return "OSINTube - Real-Time Guard"

if __name__ == "__main__":
    print(create_fancy_title())
