Execution Workflow and Commands
1. Set Credentials (Run Once)
Before running any tests or UI, store your login credentials securely:

bash
python utils/set_credentials.py
Enter your login ID and password when prompted.

Credentials are saved in OS keyring for later use.

2. Run the UI Application
Start the graphical interface for interactive serial communication:

bash
python ui.py
Enter serial port and baudrate when prompted.

Click Login to authenticate using stored credentials.

Click Run dmesg (or any command button you add) to execute commands and view logs.

3. Run Test Scripts via Test Runner
Run automated tests from the command line:

bash
python test_runner.py tests/test_login.py
or

bash
python test_runner.py tests/test_dmesg.py
These scripts use stored credentials.

They perform login checks and run commands.

Logs are saved in timestamped folders under logs/.

4. Project Setup (Optional)
To install dependencies:

bash
pip install -r requirements.txt
To install the package locally (editable mode):

bash
pip install -e .
