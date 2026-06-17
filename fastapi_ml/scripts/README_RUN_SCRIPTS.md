 Scripts to help install Visual Studio components needed to build pandas on Windows.

Files:
- install_vswhere.ps1 — downloads vswhere.exe to C:\Program Files (x86)\Microsoft Visual Studio\Installer\
- install_vs_buildtools.ps1 — downloads and runs Visual Studio Build Tools installer (C++ workload). Requires admin and may take a while.

Usage (run PowerShell as Administrator):

1. To only provide vswhere (quick):
   powershell -ExecutionPolicy Bypass -File .\scripts\install_vswhere.ps1

2. To download and install Build Tools (recommended):
   powershell -ExecutionPolicy Bypass -File .\scripts\install_vs_buildtools.ps1

After running and (if required) restarting, reactivate your venv and run:

```
(.venv) PS> pip install -r requirements.txt
```

If you prefer Conda instead, install Miniconda and create an environment with Python 3.11, then install binary packages from conda-forge.