import sys
import subprocess

# List your required packages here
required = [
    "pandas",
    "selenium",
    "tqdm",
    "openpyxl",
    "tenacity",
    # "GPT_RAND",  # Uncomment if available via pip
]

def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Package '{package}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for pkg in required:
    # Some packages have different import names (e.g., openpyxl, tenacity)
    # If so, use the import name, not the pip name
    import_name = pkg
    if pkg == "selenium":
        import_name = "selenium"
    elif pkg == "openpyxl":
        import_name = "openpyxl"
    elif pkg == "tqdm":
        import_name = "tqdm"
    elif pkg == "tenacity":
        import_name = "tenacity"
    elif pkg == "pandas":
        import_name = "pandas"
    # elif pkg == "GPT_RAND":
    #     import_name = "GPT_RAND"
    install_and_import(import_name)

# Now run your main script
import runpy
runpy.run_path("scrape_and_summ.py")
