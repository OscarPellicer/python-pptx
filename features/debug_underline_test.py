# debug_underline_test.py

import sys
import os

# Add the project root to sys.path so Python can find 'features'
# and the 'tests' directory for 'helpers'
script_dir = os.path.dirname(os.path.abspath(__file__))
# script_dir is .../python-pptx/features
project_root = os.path.dirname(script_dir)  # This should be your 'python-pptx' directory

# Ensure project_root is in sys.path for 'from features.steps...'
if project_root not in sys.path:
    sys.path.append(project_root)

# Assuming helpers.py is in 'project_root/tests/helpers.py'
# Add 'project_root/tests' to sys.path so 'from helpers import ...' works from font.py
tests_dir_path = os.path.join(project_root, "tests")
if os.path.isdir(tests_dir_path) and tests_dir_path not in sys.path:
    sys.path.append(tests_dir_path) # Append instead of insert
elif not os.path.isdir(tests_dir_path):
    print(f"Warning: Assumed 'tests' directory not found at {tests_dir_path}. "
          "The import of 'helpers' might still fail.")

# Add features/steps to sys.path because helpers.py is located there
features_steps_path = os.path.join(project_root, "features", "steps")
if os.path.isdir(features_steps_path) and features_steps_path not in sys.path:
    sys.path.append(features_steps_path)
elif not os.path.isdir(features_steps_path):
    print(f"Warning: 'features/steps' directory not found at {features_steps_path}. "
          "The import of 'helpers' from font.py will likely fail.")


# --- Imports ---
# These imports should now work if sys.path is set up correctly.
from features.steps.font import (
    given_run_with_underline_set_to_state,
    then_font_underline_is_value,
)
from behave.runner import Context as BehaveContext

# Imports used by the step definition functions, even if not directly in this script:
from pptx import Presentation
from pptx.enum.text import MSO_UNDERLINE
# 'test_pptx' will be imported from 'helpers' module by font.py
# from helpers import test_pptx # Not directly imported here anymore

# --- Context Setup ---
# Behave step functions expect a behave.runner.Context object.
class DummyRunnerConfig:
    def __init__(self):
        self.userdata = {}
        # Add other common config attributes if accessed by steps via context.config
        self.verbose = False
        self.stdout_capture = True # Behave defaults
        self.stderr_capture = True # Behave defaults
        self.log_capture = True    # Behave defaults
        self.logging_format = None
        self.logging_datefmt = None
        self.logging_level = None
        self.summary = True


class DummyRunner:
    def __init__(self):
        self.config = DummyRunnerConfig()
        self.hooks = {}
        # Add other common runner attributes if accessed by steps via context.runner
        self.feature = None
        self.capture_controller = None # For stdout/stderr capturing if steps interact

context = BehaveContext(runner=DummyRunner())
context.font = None # Initialize the attribute our steps will use

# --- Scenario Data (from the failing example) ---
underline_state_arg = "off"
expected_value_arg_str = "False" # This is how it appears in the feature file

# --- Execute "Given" Step ---
print(f"Executing: Given a font with underline set '{underline_state_arg}'")
# Call the actual 'Given' step function
given_run_with_underline_set_to_state(context, underline_state_arg)

if not hasattr(context, 'font') or context.font is None:
    print("ERROR: context.font was not set by the 'Given' step simulation.")
    print("Please ensure your 'Given' step logic is correctly replicated or called.")
else:
    print(f"After 'Given' step, context.font is: {context.font}")
    if hasattr(context.font, '_rPr') and hasattr(context.font._rPr, 'xml'):
        print(f"  Font _rPr XML after 'Given': {context.font._rPr.xml}")

    # --- Execute "Then" Step ---
    print(f"\nExecuting: Then font.underline is '{expected_value_arg_str}'")
    # Call the actual 'Then' step function
    try:
        then_font_underline_is_value(context, expected_value_arg_str)
        print("  Assertion in 'Then' step passed!")
    except AssertionError as e:
        print(f"  Assertion in 'Then' step FAILED: {e}")
    except Exception as e:
        print(f"  An unexpected error occurred in 'Then' step: {e}")

print("\nDebug script finished.")
