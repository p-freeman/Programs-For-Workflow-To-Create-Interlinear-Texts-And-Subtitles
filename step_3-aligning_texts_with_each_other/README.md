# Interlinear Text Creator v5

A desktop application for creating interlinear texts (word-by-word translations) that can be exported for:
- Desktop viewing (HTML)
- **Android Interlinear Language Learning App** (mobile-optimized HTML + ZIP package)

## Installation on Linux Mint Debian Edition

### Prerequisites

1. **Python 3** (usually pre-installed):
   ```bash
   python3 --version
   ```

2. **Tkinter** (for GUI):
    ```bash
    sudo apt update
    sudo apt install python3-tk
    ```

3. **pip** (Python package manager):
    ```bash
    sudo apt install python3-pip
    ```

### Installation

1. **Install Python dependencies**:
    ```bash
    cd step_3-aligning_texts_with_each_other
    pip3 install -r requirements.txt
    ```
## Usage
### Starting the Application

```bash
cd step_3-aligning_texts_with_each_other
python3 -m interlinear.app
```

### Exporting for Android App

- Click **"📱 Export for Android App"** - Creates mobile HTML only
- Click **"📦 Create App Package (ZIP)"** - Creates complete import package

The ZIP file can be directly imported into the Interlinear Language Learning App.


---

## Folder Structure

After copying all files, your folder should look like this:

```bash
step_3-aligning_texts_with_each_other/
├── requirements.txt
├── run.sh
├── README.md
└── interlinear/
   ├── init.py
   ├── app.py
   ├── alignment.py
   ├── dictionary.py
   ├── gui.py
   ├── project_io.py
   ├── undo.py
└── exporter/
   ├── init.py
   └── html_export.py
```
