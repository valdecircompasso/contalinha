#!/usr/bin/env python3
"""
Build script for Conta Linha Script.
This script creates an executable from contalinha.py using PyInstaller,
optionally commits and pushes changes to GitHub, and can create a new GitHub release.
"""

import os
import sys
import subprocess
import argparse
import json
import requests
from datetime import datetime

def check_requirements():
    """Check if required packages are installed."""
    required_packages = {
        "PyInstaller": False,
        "requests": False
    }
    
    # Check PyInstaller
    try:
        import PyInstaller
        required_packages["PyInstaller"] = True
        print("PyInstaller is installed.")
    except ImportError:
        print("PyInstaller is not installed. Will install it.")
    
    # Check requests
    try:
        import requests
        required_packages["requests"] = True
        print("Requests is installed.")
    except ImportError:
        print("Requests is not installed. Will install it.")
    
    # Install missing packages
    for package, installed in required_packages.items():
        if not installed:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package.lower()])
            print(f"{package} installed successfully.")

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable...")
    
    # Create a build directory if it doesn't exist
    if not os.path.exists("build"):
        os.makedirs("build")
    
    # Use PyInstaller as a Python module instead of a command
    try:
        # Use the Python executable to run PyInstaller as a module
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "PyInstaller",
                "--onefile",
                "--name=contalinha",
                "--clean",
                "contalinha.py"
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Executable created successfully in the 'dist' folder")
        else:
            print("Error building executable:")
            print(result.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error running PyInstaller: {e}")
        sys.exit(1)

def get_repo_info():
    """Get repository owner and name from remote URL."""
    try:
        # Get the remote URL
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("Could not get remote URL. Make sure this is a Git repository.")
            return None, None
        
        remote_url = result.stdout.strip()
        
        # Parse the URL to extract owner and repo name
        # Handle different URL formats:
        # https://github.com/owner/repo.git
        # git@github.com:owner/repo.git
        if remote_url.startswith("https://"):
            parts = remote_url.split("/")
            owner = parts[-2]
            repo = parts[-1].replace(".git", "")
        elif remote_url.startswith("git@"):
            parts = remote_url.split(":")
            owner_repo = parts[1].replace(".git", "")
            owner, repo = owner_repo.split("/")
        else:
            print(f"Unsupported remote URL format: {remote_url}")
            return None, None
        
        return owner, repo
    except Exception as e:
        print(f"Error getting repository information: {e}")
        return None, None

def git_operations(commit_msg):
    """Perform Git operations: add, commit, and push."""
    print("Performing Git operations...")
    
    # Check if this is a Git repository
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("This is not a Git repository. Skipping Git operations.")
        return
    
    # Add files to Git
    print("Adding files to Git...")
    subprocess.run(["git", "add", "contalinha.py", "README.md", ".gitignore"])
    
    # Add the dist directory if it exists
    if os.path.exists("dist"):
        subprocess.run(["git", "add", "dist/contalinha.exe"])
    
    # Commit changes
    print(f"Committing with message: {commit_msg}")
    result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        capture_output=True,
        text=True
    )
    
    if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
        print("No changes to commit.")
        return
    
    # Push to GitHub
    print("Pushing to GitHub...")
    result = subprocess.run(
        ["git", "push"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("Changes pushed to GitHub successfully.")
    else:
        print("Error pushing to GitHub:")
        print(result.stderr)

def create_github_release(version, token, message=None):
    """Create a new GitHub release and upload the executable."""
    owner, repo = get_repo_info()
    if not owner or not repo:
        print("Could not determine repository owner and name. Skipping release creation.")
        return False
    
    print(f"Creating release for {owner}/{repo}...")
    
    # Set release description
    if not message:
        message = f"Release {version}"
    
    # Create the release
    release_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    release_data = {
        "tag_name": version,
        "name": f"Version {version}",
        "body": message,
        "draft": False,
        "prerelease": False
    }
    
    try:
        response = requests.post(release_url, headers=headers, data=json.dumps(release_data))
        response.raise_for_status()
        release_info = response.json()
        print(f"Release created: {release_info['html_url']}")
        
        # Upload the executable as an asset
        upload_url = release_info["upload_url"].split("{")[0]
        asset_path = os.path.join("dist", "contalinha.exe")
        
        if not os.path.exists(asset_path):
            print(f"Executable not found at {asset_path}. Skipping upload.")
            return True
        
        print(f"Uploading executable to release...")
        
        with open(asset_path, "rb") as file:
            upload_headers = headers.copy()
            upload_headers["Content-Type"] = "application/octet-stream"
            upload_response = requests.post(
                f"{upload_url}?name=contalinha.exe",
                headers=upload_headers,
                data=file
            )
            upload_response.raise_for_status()
            
        print(f"Executable uploaded successfully to the release.")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error creating GitHub release: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return False

def main():
    """Main function to parse arguments and execute the build process."""
    parser = argparse.ArgumentParser(
        description="Build executable for Conta Linha Script and manage GitHub repository"
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Commit and push to GitHub after building"
    )
    parser.add_argument(
        "--message",
        default=f"Update executable - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        help="Commit message (default: 'Update executable - YYYY-MM-DD HH:MM')"
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Create a new GitHub release with the executable"
    )
    parser.add_argument(
        "--version",
        default=datetime.now().strftime("%Y.%m.%d"),
        help="Version number for the release (default: YYYY.MM.DD)"
    )
    parser.add_argument(
        "--token",
        help="GitHub personal access token for creating releases"
    )
    args = parser.parse_args()
    
    # Check requirements
    check_requirements()
    
    # Build the executable
    build_executable()
    
    # Perform Git operations if requested
    if args.commit:
        git_operations(args.message)
    
    # Create GitHub release if requested
    if args.release:
        if not args.token:
            token = os.environ.get("GITHUB_TOKEN")
            if not token:
                print("No GitHub token provided. Please provide a token using --token or set the GITHUB_TOKEN environment variable.")
                sys.exit(1)
        else:
            token = args.token
        
        create_github_release(args.version, token, args.message)

if __name__ == "__main__":
    main()
