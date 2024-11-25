import os
import subprocess
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import time


def log_message(message, status="INFO"):
    """Logs a message with a timestamp and status to the log panel."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text.configure(state="normal")  # Enable writing to log panel
    log_text.insert(tk.END, f"[{timestamp}] [{status}] {message}\n")
    log_text.see(tk.END)  # Auto-scroll
    log_text.configure(state="disabled")  # Set back to read-only


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
    """Refreshes the list of modified files and enables/disables the 'Generate and Push' button."""
    selected_repo = repo_var.get()
    if not os.path.isdir(selected_repo):
        log_message(f"Invalid repository path: {selected_repo}", "ERROR")
        return

    modified_files = get_modified_files(selected_repo)

    # Update the file list below the buttons
    file_list_text.configure(state="normal")  # Enable writing to modified files panel
    file_list_text.delete("1.0", tk.END)  # Clear the current list
    if modified_files:
        for file in modified_files:
            file_list_text.insert(tk.END, f"{file}\n")
        button.config(state=tk.NORMAL)  # Enable the 'Generate and Push' button
    else:
        file_list_text.insert(tk.END, "No modified files found.\n")
        button.config(state=tk.DISABLED)  # Disable the 'Generate and Push' button
    file_list_text.configure(state="disabled")  # Set back to read-only
    log_message("Modified files list refreshed.", "INFO")


def enable_refresh_button(event):
    """Enables the refresh button once a repository is selected."""
    refresh_button.config(state=tk.NORMAL)


def update_progress(step, total_steps):
    """Update the progress bar based on the current step and display percentage."""
    progress_value = (step / total_steps) * 100
    progress_bar["value"] = progress_value
    progress_label.config(text=f"Progress: {progress_value:.0f}%")
    root.update_idletasks()


def clone_repository():
    """Clones a GitHub repository into the specified directory."""
    repo_url = clone_url_entry.get().strip()
    if not repo_url:
        log_message("Repository URL cannot be empty.", "ERROR")
        return

    destination_dir = base_path
    log_message(f"Cloning repository from {repo_url} into {destination_dir}...")
    try:
        subprocess.run(["git", "clone", repo_url], cwd=destination_dir, check=True)
        log_message("Repository cloned successfully.", "SUCCESS")
        refresh_repo_list()  # Refresh the dropdown with the new repository
    except subprocess.CalledProcessError as e:
        log_message(f"Failed to clone repository: {e}", "ERROR")


def refresh_repo_list():
    """Refreshes the repository list in the dropdown."""
    repos = get_git_repos(base_path)
    repo_dropdown["values"] = repos
    repo_dropdown["width"] = calculate_combobox_width(repos)
    log_message("Repository list refreshed.", "INFO")


def generate_and_push():
    """Stages, commits, and pushes changes in the selected repository."""
    try:
        # Disable the button
        button.config(state=tk.DISABLED)

        # Clear the log and reset the progress bar
        log_text.configure(state="normal")  # Enable writing to log panel
        log_text.delete("1.0", tk.END)
        log_text.configure(state="disabled")  # Set back to read-only
        progress_bar["value"] = 0
        progress_label.config(text="Progress: 0%")

        # Get the selected repository path
        selected_repo = repo_var.get()
        if not os.path.isdir(selected_repo):
            raise Exception(f"The selected path '{selected_repo}' is not valid.")

        log_message(f"Selected repository path: {selected_repo}")
        branch = "main"  # Branch name

        # Get the commit message
        commit_message = commit_msg_text.get("1.0", tk.END).strip()
        if not commit_message:  # Use default message if none provided
            commit_message = "Automatic commit: Updated repository"

        log_message("Process started.")
        start_time = time.time()

        total_steps = 4  # Define the total number of steps

        # Step 1: Stage all changes
        log_message("Staging all changes in the repository...")
        update_progress(1, total_steps)
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

        # Step 2: Commit changes
        log_message(f"Committing changes with message: '{commit_message}'...")
        update_progress(2, total_steps)
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=selected_repo,
            check=True
        )
        log_message(f"Changes committed with message: '{commit_message}'", "SUCCESS")

        # Step 3: Push changes
        log_message(f"Pushing changes to branch: {branch}...")
        update_progress(3, total_steps)
        subprocess.run(["git", "push", "origin", branch], cwd=selected_repo, check=True)
        log_message(f"Changes pushed to branch '{branch}' successfully!", "SUCCESS")

        # Final Step: Complete the process
        elapsed_time = time.time() - start_time
        log_message(f"Process completed successfully in {elapsed_time:.2f} seconds!", "SUCCESS")
        update_progress(total_steps, total_steps)
    except subprocess.CalledProcessError as e:
        log_message(f"Git operation failed: {e}", "ERROR")
    except Exception as e:
        log_message(f"An error occurred: {e}", "ERROR")
    finally:
        # Re-enable the button if changes exist
        refresh_modified_files()


# GUI setup
root = tk.Tk()
root.title("Git Automation Tool")

# Left panel: Repository selection and actions
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

repo_label = tk.Label(left_frame, text="Select Repository:")
repo_label.pack(pady=5)

repo_var = tk.StringVar()
repo_dropdown = ttk.Combobox(left_frame, textvariable=repo_var, state="readonly")
base_path = "C:/Users/shsa0222/Desktop/DevOps"  # Change this to your base path
repos = get_git_repos(base_path)
repo_dropdown["values"] = repos
repo_dropdown["width"] = calculate_combobox_width(repos)
repo_dropdown.pack(pady=5)
repo_dropdown.bind("<<ComboboxSelected>>", enable_refresh_button)

commit_msg_label = tk.Label(left_frame, text="Commit Message (Optional):")
commit_msg_label.pack(pady=5)

commit_msg_text = tk.Text(left_frame, height=3, width=50)
commit_msg_text.pack(pady=5)

button = tk.Button(left_frame, text="Generate and Push", command=generate_and_push, state=tk.DISABLED)
button.pack(pady=10)

refresh_button = tk.Button(left_frame, text="Refresh Modified Files", command=refresh_modified_files, state=tk.DISABLED)
refresh_button.pack(pady=5)

file_list_label = tk.Label(left_frame, text="Modified Files:")
file_list_label.pack(pady=5)

file_list_text = tk.Text(left_frame, height=10, width=50, state="disabled")
file_list_text.pack(pady=5)

# Clone Repository
clone_label = tk.Label(left_frame, text="Clone Repository (GitHub URL):")
clone_label.pack(pady=5)

clone_url_entry = tk.Entry(left_frame, width=50)
clone_url_entry.pack(pady=5)

clone_button = tk.Button(left_frame, text="Clone Repository", command=clone_repository)
clone_button.pack(pady=10)

# Right panel: Log and Progress bar
right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

log_label = tk.Label(right_frame, text="Log:")
log_label.pack(pady=5)

log_text = tk.Text(right_frame, height=25, width=80, state="disabled")
log_text.pack(pady=5)

progress_label = tk.Label(right_frame, text="Progress: 0%")
progress_label.pack(pady=5)

progress_bar = ttk.Progressbar(right_frame, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=5)

refresh_repo_list()  # Populate the dropdown with the initial repository list
root.mainloop()
