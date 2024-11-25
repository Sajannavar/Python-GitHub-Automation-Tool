import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter import ttk
import subprocess
import os
import threading

class GitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Operations")
        self.root.geometry("700x500")

        # Repository Path and Branch
        self.repo_path = None
        self.current_branch = None

        # Base directory containing multiple repositories
        self.base_repo_path = None

        # GitHub Authentication
        self.github_token = None

        # Initialize UI Components
        self.create_widgets()

    def create_widgets(self):
        # Base Repo Directory Selection
        self.select_base_repo_button = tk.Button(self.root, text="Select Base Repo Directory", command=self.select_base_repo)
        self.select_base_repo_button.pack(pady=10)

        # Repo Selection from Base Directory
        self.repo_label = tk.Label(self.root, text="Select Repo:")
        self.repo_label.pack()

        self.repo_combobox = ttk.Combobox(self.root)
        self.repo_combobox.pack(pady=5)
        self.repo_combobox.bind("<<ComboboxSelected>>", self.on_repo_selected)

        # Branch Selection
        self.branch_label = tk.Label(self.root, text="Select Branch:")
        self.branch_label.pack()

        self.branch_combobox = ttk.Combobox(self.root)
        self.branch_combobox.pack(pady=5)
        self.branch_combobox.config(state=tk.DISABLED)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="indeterminate")
        self.progress.pack(pady=10)

        # Log Text Box
        self.log_text = tk.Text(self.root, height=8, width=70)
        self.log_text.pack(pady=10)
        self.log_text.config(state=tk.DISABLED)

        # Git Operations Buttons
        self.git_config_button = tk.Button(self.root, text="Git Config", command=self.git_config)
        self.git_config_button.pack(pady=5)

        self.git_clone_button = tk.Button(self.root, text="Git Clone", command=self.git_clone)
        self.git_clone_button.pack(pady=5)

        self.git_add_button = tk.Button(self.root, text="Git Add", command=self.git_add)
        self.git_add_button.pack(pady=5)

        self.git_commit_button = tk.Button(self.root, text="Git Commit", command=self.git_commit)
        self.git_commit_button.pack(pady=5)

        self.git_push_button = tk.Button(self.root, text="Git Push", command=self.git_push)
        self.git_push_button.pack(pady=5)

        self.git_pull_button = tk.Button(self.root, text="Git Pull", command=self.git_pull)
        self.git_pull_button.pack(pady=5)

        self.git_branch_button = tk.Button(self.root, text="Git Branch", command=self.git_branch)
        self.git_branch_button.pack(pady=5)

        self.git_merge_button = tk.Button(self.root, text="Git Merge", command=self.git_merge)
        self.git_merge_button.pack(pady=5)

        # GitHub Token Authentication Button
        self.git_auth_button = tk.Button(self.root, text="Authenticate with GitHub", command=self.authenticate_github)
        self.git_auth_button.pack(pady=10)

    def update_log(self, message):
        """Update the log in the text box."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.yview(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def run_git_command(self, command):
        """Run Git commands and log output."""
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True, cwd=self.repo_path)
            self.update_log(result.stdout)
            self.update_log(result.stderr)
        except subprocess.CalledProcessError as e:
            self.update_log(f"Error: {e.stderr}")

    def run_command_with_progress(self, command):
        """Run a long-running Git command (like clone or pull) with progress indication."""
        self.progress.start()
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True, cwd=self.repo_path)
            self.update_log(result.stdout)
            self.update_log(result.stderr)
        except subprocess.CalledProcessError as e:
            self.update_log(f"Error: {e.stderr}")
        finally:
            self.progress.stop()

    def select_base_repo(self):
        """Allow user to select the base directory where multiple repos are stored."""
        self.base_repo_path = filedialog.askdirectory(title="Select Base Repo Directory")
        if self.base_repo_path:
            self.update_log(f"Selected base repo directory: {self.base_repo_path}")
            self.update_repo_list()

    def update_repo_list(self):
        """Fetch and display a list of repositories from the base directory."""
        if not self.base_repo_path:
            return

        # Get all directories in the base directory that are git repositories
        repos = [f for f in os.listdir(self.base_repo_path) if os.path.isdir(os.path.join(self.base_repo_path, f)) and os.path.exists(os.path.join(self.base_repo_path, f, ".git"))]
        
        if repos:
            self.repo_combobox['values'] = repos
            self.repo_combobox.set(repos[0])  # Select first repo by default
        else:
            self.repo_combobox['values'] = []
            messagebox.showerror("Error", "No Git repositories found in the selected directory.")

    def on_repo_selected(self, event):
        """Handle repo selection and enable branch selection."""
        repo_name = self.repo_combobox.get()
        self.repo_path = os.path.join(self.base_repo_path, repo_name)

        if self.repo_path and os.path.isdir(self.repo_path):
            self.update_log(f"Selected repository: {self.repo_path}")
            self.update_branch_list()

    def update_branch_list(self):
        """Fetch and display branches of the selected repo."""
        if not self.repo_path:
            return

        branches = subprocess.run(["git", "branch", "-r"], cwd=self.repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if branches.returncode == 0:
            branch_list = [branch.strip() for branch in branches.stdout.splitlines()]
            self.branch_combobox['values'] = branch_list
            if branch_list:
                self.branch_combobox.set(branch_list[0])
            self.branch_combobox.config(state=tk.NORMAL)
        else:
            self.update_log("Failed to fetch branches.")
            self.branch_combobox.config(state=tk.DISABLED)

    def git_config(self):
        """Run the git config command."""
        self.run_git_command(["git", "config", "--list"])

    def git_clone(self):
        """Perform git clone operation."""
        clone_url = simpledialog.askstring("Clone URL", "Enter the Git repository URL:")
        if clone_url:
            threading.Thread(target=self.clone_repo, args=(clone_url,)).start()

    def clone_repo(self, clone_url):
        """Clone the repository using Git."""
        self.update_log(f"Cloning repository from {clone_url}...")
        self.run_command_with_progress(["git", "clone", clone_url])

    def git_add(self):
        """Add changes to the staging area."""
        if self.repo_path:
            self.run_git_command(["git", "add", "."])

    def git_commit(self):
        """Commit changes to the repository."""
        commit_msg = simpledialog.askstring("Commit Message", "Enter commit message:")
        if commit_msg and self.repo_path:
            self.run_git_command(["git", "commit", "-m", commit_msg])

    def git_push(self):
        """Push changes to the remote repository."""
        if self.repo_path:
            if self.github_token:
                self.update_log("Authenticating with GitHub for push...")
                self.run_git_command(["git", "push", f"https://{self.github_token}@github.com/yourusername/yourrepo.git"])
            else:
                self.run_git_command(["git", "push"])

    def git_pull(self):
        """Pull latest changes from the remote repository."""
        if self.repo_path:
            self.run_command_with_progress(["git", "pull"])

    def git_branch(self):
        """Display current branches and manage them."""
        if self.repo_path:
            self.run_git_command(["git", "branch"])

    def git_merge(self):
        """Merge a selected branch into the current branch."""
        if self.repo_path:
            target_branch = self.branch_combobox.get()
            if target_branch:
                self.run_git_command(["git", "merge", target_branch])

    def authenticate_github(self):
        """Authenticate GitHub with a personal access token (PAT)."""
        token = simpledialog.askstring("GitHub Token", "Enter your GitHub Personal Access Token:")
        if token:
            self.github_token = token
            self.update_log("GitHub authentication successful!")

if __name__ == "__main__":
    root = tk.Tk()
    app = GitApp(root)
    root.mainloop()
