"""
Prints the machine, software and model settings needed for the report's setup table.
Read-only. Run from backend\\backend:   python collect_env_info.py
Only an allow-list of non-secret .env settings is printed (no keys, no tokens).
"""
import os, platform, subprocess, sys, json
from importlib import metadata

def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return (r.stdout or r.stderr).strip() or "(no output)"
    except Exception as e:
        return f"(not available: {e})"

def ps(command):
    return run(["powershell", "-NoProfile", "-Command", command])

print("== MACHINE ==")
print("OS (python):", platform.platform())
print("OS:", ps("(Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version | Format-List | Out-String).Trim()"))
print("CPU:", ps("(Get-CimInstance Win32_Processor | Select-Object -First 1 Name, NumberOfCores, NumberOfLogicalProcessors | Format-List | Out-String).Trim()"))
print("RAM (GB):", ps("[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,1)"))
print("GPU:", ps("(Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name) -join '; '"))

print("\n== SOFTWARE ==")
print("Python:", sys.version.split()[0])
for pkg in ["fastapi", "uvicorn", "pydantic", "requests", "python-dotenv", "onnxruntime", "onnx",
            "transformers", "tokenizers", "numpy", "torch"]:
    try:
        print(f"{pkg}: {metadata.version(pkg)}")
    except Exception:
        print(f"{pkg}: not installed")
print("Ollama:", run(["ollama", "--version"]))
print("Node:", run(["node", "--version"]))
print("npm:", run(["npm", "--version"]))
for base in ("../../frontend", "frontend"):
    p = os.path.join(base, "node_modules", "next", "package.json")
    if os.path.exists(p):
        print("Next.js (installed):", json.load(open(p, encoding="utf-8")).get("version"))
        break
else:
    print("Next.js: run this from backend\\backend after npm install, or read frontend\\package.json")

print("\n== MODEL SETTINGS ==")
print("ollama show llama3.2:1b:\n" + run(["ollama", "show", "llama3.2:1b"]))
allow = {"OLLAMA_MODEL", "INJECTION_DETECTOR", "INJECTION_THRESHOLD", "TOXICITY_MODE", "GUARDRAIL_ENABLED"}
if os.path.exists(".env"):
    for line in open(".env", encoding="utf-8"):
        key = line.split("=", 1)[0].strip()
        if key in allow:
            print(".env:", line.strip())
if os.path.isdir("models"):
    for root, _, files in os.walk("models"):
        for f in files:
            fp = os.path.join(root, f)
            print(f"model file: {fp}  {os.path.getsize(fp) / 1e6:.0f} MB")

print("\n== GIT ==")
print("branch:", run(["git", "rev-parse", "--abbrev-ref", "HEAD"]))
print("HEAD:", run(["git", "rev-parse", "--short", "HEAD"]))
print("v1-submitted tag:", run(["git", "rev-parse", "--short", "v1-submitted"]))
print("uncommitted/untracked entries:", len(run(["git", "status", "--porcelain"]).splitlines()))
