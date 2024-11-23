# Python-GitHub-Automation-Tool
Here's a sample `README.md` file for your Git Automation Tool:

---

# Git Automation Tool

A simple and efficient **Git Automation Tool** built with Python and Tkinter to manage Git repositories with ease. This tool allows you to clone repositories, manage branches, view modified files, and push changes—all through a user-friendly graphical interface.

## Features

- **Clone Repository**: Clone any GitHub repository into a specified base directory using the repository URL.
- **Select Repository**: Dropdown menu to browse Git repositories within a base directory.
- **Branch Management**: Dynamically select and manage branches of the selected repository.
- **View Modified Files**: List uncommitted changes in the selected branch of a repository.
- **Automated Git Workflow**:
  - Stage changes.
  - Commit with a custom or default message.
  - Push changes to the selected branch.
- **Detailed Logs**: View operation logs with timestamps and statuses.

---

## Installation and Setup

### Prerequisites
- Python 3.7 or higher
- Git installed and accessible via the command line
- Tkinter (usually pre-installed with Python)
- A GitHub account

### Clone the Project
```bash
git clone <your-repo-url>
cd <project-directory>
```

---

## Usage

### Running the Application
1. Launch the application:
    ```bash
    python app.py
    ```
2. The GUI will open, displaying options for managing Git repositories.

### Features Walkthrough

#### 1. Clone a Repository
- Enter the **GitHub repository URL** in the "Clone GitHub Repository" section.
- Click **Clone Repository**.
- The repository will be cloned into the configured base directory (default: `C:/Users/shsa0222/Desktop/DevOps`).

#### 2. Select a Repository
- Use the dropdown menu under "Select Repository" to choose a repository from the base directory.
- The tool will automatically detect and display available repositories.

#### 3. Manage Branches
- After selecting a repository, choose a branch from the "Select Branch" dropdown menu.

#### 4. View Modified Files
- Click **Refresh Modified Files** to see a list of uncommitted changes in the selected branch.

#### 5. Commit and Push Changes
- Enter a **commit message** (optional).
- Click **Generate and Push** to stage, commit, and push changes to the selected branch.
- Logs will display the operation status.

---

## File Structure

```plaintext
.
├── app.py          # Main Python application
├── README.md       # Documentation (this file)
└── requirements.txt # Optional (if dependencies are added)
```

---

## Customization

### Change Base Directory
To modify the base directory where repositories are managed:
1. Open `app.py`.
2. Locate the `base_path` variable (default: `C:/Users/shsa0222/Desktop/DevOps`).
3. Update it to your preferred directory:
   ```python
   base_path = "/path/to/your/directory"
   ```

---

## Dependencies

- Tkinter (GUI library for Python)
- Git (command-line tool)

---

## Screenshots

![Main GUI](https://via.placeholder.com/500x300?text=Main+GUI)  
*Screenshot of the main interface.*

---

## Contributing

Contributions are welcome!  
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with detailed changes.

---

## Author

**Shubham Sajannavar**  
[LinkedIn](https://www.linkedin.com/in/shubham-sajannavar/)  

---

## License

This project is licensed under the MIT License.  

---

Let me know if you'd like to add screenshots, badges, or further sections!