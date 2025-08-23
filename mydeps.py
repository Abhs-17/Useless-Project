

import subprocess
import sys
import argparse
import importlib
from colorama import Fore, Style, init

# Initialize color output for Windows/Mac/Linux
init(autoreset=True)

def is_installed(package):
    """Check if a package is already installed."""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def install_from_file(filename):
    """Install packages listed in the requirements file."""
    try:
        with open(filename) as file:
            for line in file:
                dep = line.strip()
                if dep and not dep.startswith("#"):
                    pkg_name = dep.split("==")[0]  # Remove version for check
                    if is_installed(pkg_name):
                        print(Fore.GREEN + f"✅ {pkg_name} is already installed. Skipping...")
                    else:
                        print(Fore.CYAN + f"📦 Installing {dep}...")
                        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
    except FileNotFoundError:
        print(Fore.RED + f"❌ Requirements file '{filename}' not found. Please create it.")

def uninstall_from_file(filename):
    """Uninstall packages listed in the requirements file."""
    try:
        with open(filename) as file:
            for line in file:
                dep = line.strip()
                if dep and not dep.startswith("#"):
                    pkg_name = dep.split("==")[0]
                    if is_installed(pkg_name):
                        print(Fore.YELLOW + f"🗑 Uninstalling {pkg_name}...")
                        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", pkg_name])
                    else:
                        print(Fore.GREEN + f"✅ {pkg_name} is not installed. Skipping...")
    except FileNotFoundError:
        print(Fore.RED + f"❌ Requirements file '{filename}' not found. Please create it.")

def generate_requirements(filename):
    """Generate a requirements file from currently installed packages."""
    print(Fore.CYAN + f"📝 Generating {filename} from installed packages...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        stdout=subprocess.PIPE,
        text=True
    )
    with open(filename, "w") as f:
        f.write(result.stdout)
    print(Fore.GREEN + f"✅ Requirements saved to {filename}")

def smart_import(module_name):
    """Try importing a module, install if missing."""
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        print(Fore.YELLOW + f"🚀 Module '{module_name}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
        print(Fore.GREEN + f"✅ Module '{module_name}' installed successfully.")
        return importlib.import_module(module_name)

def run_script(script_name):
    """Run a Python script, auto-installing missing modules if necessary."""
    while True:
        try:
            subprocess.check_call([sys.executable, script_name])
            break  # If script runs successfully, exit loop
        except subprocess.CalledProcessError as e:
            # Script error unrelated to imports
            raise
        except ModuleNotFoundError as e:
            missing_pkg = str(e).split("'")[1]
            print(Fore.YELLOW + f"Module '{missing_pkg}' is missing. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", missing_pkg])
            print(Fore.GREEN + f"✅ Module '{missing_pkg}' installed. Retrying...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Python dependencies.")
    parser.add_argument("command", choices=["install", "generate", "uninstall", "run"],
                        help="install: install packages from file | generate: create requirements file | uninstall: remove packages from file | run: auto-install missing packages while running a script")
    parser.add_argument("--file", "-f", default="my_requirements.txt",
                        help="Requirements file name (default: my_requirements.txt)")
    parser.add_argument("--script", "-s",
                        help="Python script to run with auto-install (used with 'run' command)")

    args = parser.parse_args()

    if args.command == "install":
        install_from_file(args.file)
    elif args.command == "generate":
        generate_requirements(args.file)
    elif args.command == "uninstall":
        uninstall_from_file(args.file)
    elif args.command == "run":
        if not args.script:
            print(Fore.RED + "❌ Please provide a script to run, e.g., python mydeps.py run -s app.py")
        else:
            run_script(args.script)
