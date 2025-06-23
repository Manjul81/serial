import subprocess
import sys
import os

def run_test_script(script_path):
    if not os.path.isfile(script_path):
        print(f"Error: Test script '{script_path}' does not exist.")
        return 1

    print(f"Running test script: {script_path}\n{'='*60}")

    # Run the test script as a subprocess using the same Python interpreter
    process = subprocess.Popen(
        [sys.executable, script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Stream output and errors live
    while True:
        output = process.stdout.readline()
        if output:
            print(output, end='')

        err = process.stderr.readline()
        if err:
            print(err, end='', file=sys.stderr)

        if output == '' and err == '' and process.poll() is not None:
            break

    exit_code = process.wait()
    print(f"\nTest script exited with code {exit_code}")
    return exit_code

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_runner.py <test_script.py>")
        sys.exit(1)

    test_script = sys.argv[1]
    exit_code = run_test_script(test_script)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
