## Jupyter standard Shortcuts

**Switch command mode:** ESC
**Change to markdown:** M
**Change to Code:** Y
**Change to Raw:** R
**Execute and move to next cell:** Shift + Enter
**Just Excute cell:** Ctrl + Enter

For example, to switch code mode to markdown: `ESC + M`

## VSCode Select Interpreter

When work on python with conda, the vs code cant auto identitfy what env you actually activated and you need to manually set the interpreter in vscode.

Press `CTRL + Shift + P` -> Type `Python: Select Interpreter` -> Select the a conda environment

## Install Python Manager Tools(similar to npm)

In order to make `utils` accessible to every module for **rag** tutorial, i need to make `rag` as local project in "editable" mode using a `setup.py` or `pyproject.toml(similar to package.json)`.

Although we can use some trick to access outer directory library, but it's not a standard way.

Setup `pyproject.toml` and make project as 'editable' will treat the entire project as a library that is 'installed' into your environment.

This make your imports work perfectly regardless of which folder your script or notebook is sitting in.

1. Create the pyproject.toml

Create a file named `pyproject.toml` in the rag folder. This tells Python: "This folder is a package named my_rag_project."

```ini
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my_rag_project"
version = "0.1.0"
description = "My RAG Learning Project"
dependencies = [
    "langchain",
    "langchain-chroma",
    "langchain-ollama"
]

[tool.setuptools.packages.find]
where = ["."]
```

2. Editable Install

Open your terminal, navigate to your `rag` folder, and run this command:
```bash
pip install -e .
```

### Q&A

1. **Do I need to define every package in the TOML?**

Technically, no, it is not strictly necessary for the code to run on your local machine if you already have those packages installed in your Conda environment.

However, it is best practice to list them. The dependencies section acts as a manual for your project. If you ever move your code to a new computer or share it with a teammate, they can simply run `pip install -e .` and Python will automatically download every library needed to make your RAG system work.

If you are using conda

```bash
conda list --export
# or
pip freeze > requirements.txt

# Recommend method: use pipdeptree
pip install pipdeptree
pipdeptree --depth 0
```

2. **Does pyproject.toml update in real-time?**

If you are using standard `pip`: No.

If you run pip install langchain, it installs the package to your environment, but it does not touch your pyproject.toml file. You would have to manually add it to the dependencies = [] list.

3. **Is there a way to automate this?**

Yes. Modern Python tools (called "Project Managers") handle this exactly like npm does for JavaScript. Instead of using pip install, you use their specific commands.

The most popular tools for this are **uv, Poetry, and PDM**.

**To Install a package and auto-update TOML**

```bash
uv add langchain
```

**To Sync your environment**
```bash
uv sync
```

**Summary**
1. Create pyproject.toml.
2. Install `pipdeptree`, `uv`
3. Initialize pyproject.toml dependencies section with `pipdeptree` command: `pipdeptree --depth 0`
4. Install new package using `uv add xxxx`
5. Last, execute `pip install -e .`