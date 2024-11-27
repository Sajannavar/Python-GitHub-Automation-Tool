import os
import subprocess
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import time


def log_message(message, status="INFO"):
    """Logs a message with a timestamp and status to the side panel."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text.insert(tk.END, f"[{timestamp}] [{status}] {message}\n")
    log_text.see(tk.END)  # Auto-scroll


def calculate_combobox_width(items):
    """Calculate the appropriate width for the combobox based on the longest item."""
    max_item_length = max(len(item) for item in items) if items else 20  # Default to 20 if empty
    return max_item_length + 2  # Add padding for readability


def get_git_repos(base_path):
    """Returns a list of Git repository directories from the base path."""
    repos = []
    for root, dirs, files in os.walk(base_path):
        if '.git' in dirs:  # Check if it's a git repository
            repos.append(root)  # Add the full path of the repository
    return repos


def get_branches(repo_path):
    """Returns a list of branches in the selected Git repository."""
    try:
        result = subprocess.run(
            ["git", "branch", "--list"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        branches = result.stdout.strip().split("\n")
        branches = [branch.strip().replace("* ", "") for branch in branches]
        return branches
    except subprocess.CalledProcessError as e:
        log_message(f"Error fetching branches: {e}", "ERROR")
        return []


def get_modified_files(repo_path):
    """Gets the list of modified files in the selected Git repository."""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        files = result.stdout.strip().split("\n")
        return [f.strip() for f in files if f]  # Filter out empty lines
    except subprocess.CalledProcessError as e:
        log_message(f"Error fetching modified files: {e}", "ERROR")
        return []


def refresh_modified_files():
    """Refresh the list of modified files displayed."""
    selected_repo = repo_var.get()
    if not os.path.isdir(selected_repo):
        log_message("Invalid repository path.", "ERROR")
        return

    modified_files = get_modified_files(selected_repo)

    # Clear the text area and update with new files
    file_list_text.delete("1.0", tk.END)
    if modified_files:
        for file in modified_files:
            file_list_text.insert(tk.END, f"{file}\n")
    else:
        file_list_text.insert(tk.END, "No modified files found.\n")
    log_message("Modified files list refreshed.", "INFO")


def update_branch_dropdown(event):
    """Update branch dropdown based on repository selection."""
    selected_repo = repo_var.get()
    if os.path.isdir(selected_repo):
        branches = get_branches(selected_repo)
        branch_dropdown["values"] = branches
        if branches:
            branch_var.set("main" if "main" in branches else branches[0])
            branch_dropdown.config(state="readonly")
        else:
            branch_var.set("")
            branch_dropdown["values"] = []
        refresh_modified_files()  # Refresh modified files for the new repository
    else:
        branch_var.set("")
        branch_dropdown["values"] = []


def generate_and_push():
    """Stages, commits, and pushes changes to the selected branch of the repository."""
    try:
        # Disable the button
        button.config(state=tk.DISABLED)

        # Clear the log
        log_text.delete("1.0", tk.END)

        # Get the selected repository and branch
        selected_repo = repo_var.get()
        branch = branch_var.get()

        if not os.path.isdir(selected_repo):
            raise Exception(f"The selected path '{selected_repo}' is not valid.")

        log_message(f"Selected repository path: {selected_repo}")
        log_message(f"Target branch: {branch}")

        # Get the commit message
        commit_message = commit_msg_text.get("1.0", tk.END).strip()
        if not commit_message:  # Use default message if none provided
            commit_message = "Automatic commit: Updated repository"

        log_message("Process started.")
        start_time = time.time()

        # Stage all changes
        log_message("Staging all changes in the repository...")
        subprocess.run(["git", "add", "."], cwd=selected_repo, check=True)
        log_message("All changes staged successfully.", "SUCCESS")

        # Check if there are any changes to commit
        check_status = subprocess.run(
            ["git", "diff", "--cached", "--exit-code"], cwd=selected_repo, capture_output=True
        )

        if check_status.returncode == 0:
            log_message("No changes to commit. Exiting.", "INFO")
            log_message("Process completed successfully.", "SUCCESS")
            return  # No changes to commit, exit early

        # Commit the changes
        log_message(f"Committing changes with message: '{commit_message}'...")
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=selected_repo,
            check=True
        )
        log_message(f"Changes committed with message: '{commit_message}'", "SUCCESS")

        # Push the changes
        log_message(f"Pushing changes to branch: {branch}...")
        subprocess.run(["git", "push", "origin", branch], cwd=selected_repo, check=True)
        log_message(f"Changes pushed to branch '{branch}' successfully!", "SUCCESS")

        elapsed_time = time.time() - start_time
        log_message(f"Process completed successfully in {elapsed_time:.2f} seconds!", "SUCCESS")
    except subprocess.CalledProcessError as e:
        log_message(f"Git operation failed: {e}", "ERROR")
    except Exception as e:
        log_message(f"An error occurred: {e}", "ERROR")
    finally:
        # Re-enable the button
        button.config(state=tk.NORMAL)


def clone_repository():
    """Clones a GitHub repository into the base path."""
    try:
        repo_url = clone_url_text.get("1.0", tk.END).strip()
        if not repo_url:
            log_message("Please enter a valid GitHub repository URL.", "ERROR")
            return

        # Clone the repository into the base path
        log_message(f"Cloning repository from {repo_url} into {base_path}...")
        subprocess.run(["git", "clone", repo_url], cwd=base_path, check=True)
        log_message(f"Repository cloned successfully from {repo_url}!", "SUCCESS")

        # Refresh the repository dropdown with the new repo
        new_repos = get_git_repos(base_path)
        repo_dropdown["values"] = new_repos
        log_message("Repository list updated.", "INFO")
    except subprocess.CalledProcessError as e:
        log_message(f"Git clone operation failed: {e}", "ERROR")
    except Exception as e:
        log_message(f"An error occurred while cloning: {e}", "ERROR")


# GUI setup
root = tk.Tk()
root.title("Git Automation Tool")

# Base path for repositories
base_path = "C:/Users/shsa0222/Desktop/DevOps"  # Change this to your base path

# Repository selection frame
repo_frame = tk.Frame(root)
repo_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

repo_label = tk.Label(repo_frame, text="Select Repository:")
repo_label.pack(pady=5)

repo_var = tk.StringVar()
repo_dropdown = ttk.Combobox(repo_frame, textvariable=repo_var, state="readonly")
repos = get_git_repos(base_path)
repo_dropdown["values"] = repos
repo_dropdown["width"] = calculate_combobox_width(repos)
repo_dropdown.pack(pady=5)
repo_dropdown.bind("<<ComboboxSelected>>", update_branch_dropdown)

branch_label = tk.Label(repo_frame, text="Select Branch:")
branch_label.pack(pady=5)

branch_var = tk.StringVar()
branch_dropdown = ttk.Combobox(repo_frame, textvariable=branch_var, state="readonly")
branch_dropdown.pack(pady=5)

commit_msg_label = tk.Label(repo_frame, text="Commit Message:")
commit_msg_label.pack(pady=5)

commit_msg_text = tk.Text(repo_frame, height=3, width=40)
commit_msg_text.pack(pady=5)

button = tk.Button(repo_frame, text="Generate and Push", command=generate_and_push)
button.pack(pady=10)

# Modified Files Section
file_list_label = tk.Label(repo_frame, text="Modified Files:")
file_list_label.pack(pady=5)

file_list_text = tk.Text(repo_frame, height=10, width=40)
file_list_text.pack(pady=5)

refresh_button = tk.Button(repo_frame, text="Refresh Modified Files", command=refresh_modified_files)
refresh_button.pack(pady=5)

# Git Clone Section
clone_label = tk.Label(repo_frame, text="Clone GitHub Repository:")
clone_label.pack(pady=5)

clone_url_text = tk.Text(repo_frame, height=2, width=40)
clone_url_text.pack(pady=5)

clone_button = tk.Button(repo_frame, text="Clone Repository", command=clone_repository)
clone_button.pack(pady=10)

# Log section
log_frame = tk.Frame(root, relief=tk.SUNKEN, borderwidth=1)
log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

log_label = tk.Label(log_frame, text="Logs:")
log_label.pack(pady=5)

log_text = tk.Text(log_frame, height=25, width=60)
log_text.pack(pady=5)

root.mainloop()
