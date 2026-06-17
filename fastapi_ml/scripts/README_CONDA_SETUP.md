Automated Conda setup script

Run as a regular user (no admin required):

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_conda_env.ps1
```

What it does:
- Downloads Miniconda installer to your TEMP folder (if missing)
- Installs Miniconda silently into `%USERPROFILE%\Miniconda3`
- Creates a conda env named `prod` with Python 3.11
- Installs `pandas`, `numpy`, `scikit-learn`, and `xgboost` from `conda-forge`
- Runs `pip install -r requirements_no_pandas.txt` inside the `prod` env to install remaining pure-Python deps

After it finishes, activate the environment:

```powershell
conda activate prod
```

Then run your app or tests.

If the script fails to find `conda` after install, open a new PowerShell window (or restart the session) and retry the `conda` commands manually.
