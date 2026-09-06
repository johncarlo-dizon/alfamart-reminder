import sys
import os

# NOTE: sys.argv[0] is used (not __file__) so this still resolves to the
# folder the .exe lives in, even when frozen by PyInstaller with --onefile.
BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
SCHEDULES_FILE = os.path.join(BASE_DIR, "schedules.json")
STORES_FILE = os.path.join(BASE_DIR, "stores.txt")
LOGS_FILE = os.path.join(BASE_DIR, "deployment_logs.txt")

# Standard Template Preset Definitions
PRESETS = {
    "eservices_login": {
        "title": "6:00 AM REMINDER!",
        "lines": "MAG LOG IN SA E-SERVICES.",
        "step1_title": "POS",
        "step1_sub": "REGULAR POS LOGIN",
        "step1_body": "Mag log in sa POS tulad ng\nnakasanayan.",
        "step2_title": "E-SERVICES",
        "step2_sub": "E-SERVICES LOGIN",
        "step2_body": "Mag log in sa E-Services\nkada Cash-In.",
        "warning": "UGALIIN MAG LOG IN AGAD SA E-SERVICES\nMATAPOS ANG POS REGULAR LOG IN\nPARA MAKAIWAS SA MGA TECHNICAL ERRORS"
    },
    "eservices_eod": {
        "title": "10:00 PM REMINDER!",
        "lines": "MAG EOD SA E-SERVICES.",
        "step1_title": "POS",
        "step1_sub": "REGULAR POS EOD",
        "step1_body": "Mag EOD sa POS tulad ng\nnakasanayan.",
        "step2_title": "E-SERVICES",
        "step2_sub": "E-SERVICES EOD",
        "step2_body": "Mag EOD sa E-Services.",
        "warning": "UGALIIN MAG EOD SA E-SERVICES\nMATAPOS ANG POS REGULAR EOD\nPARA MAKAIWAS SA MGA TECHNICAL ERRORS"
    }
}

DEFAULT_TEMPLATES = [
    {
        "time": "03:00",
        "title": "03:00 am Reminder",
        "type": "standard",
        "lines": "1. Proceed sa Cash Pick-Up!\n2. Laging isara ang storage door\n3. Siguraduhing naka-combination mode ang vault.",
        "step1_title": "POS",
        "step1_sub": "REGULAR POS LOGIN",
        "step1_body": "Mag log in sa POS tulad ng\nnakasanayan.",
        "step2_title": "E-SERVICES",
        "step2_sub": "E-SERVICES LOGIN",
        "step2_body": "Mag log in sa E-Services\nkada Cash-In.",
        "warning": "UGALIIN MAG LOG IN AGAD SA E-SERVICES\nMATAPOS ANG POS REGULAR LOG IN\nPARA MAKAIWAS SA MGA TECHNICAL ERRORS"
    },
    {
        "time": "06:00",
        "title": "6:00 AM REMINDER!",
        "type": "eservices_login",
        "lines": "MAG LOG IN SA E-SERVICES.",
        "step1_title": "POS",
        "step1_sub": "REGULAR POS LOGIN",
        "step1_body": "Mag log in sa POS tulad ng\nnakasanayan.",
        "step2_title": "E-SERVICES",
        "step2_sub": "E-SERVICES LOGIN",
        "step2_body": "Mag log in sa E-Services\nkada Cash-In.",
        "warning": "UGALIIN MAG LOG IN AGAD SA E-SERVICES\nMATAPOS ANG POS REGULAR LOG IN\nPARA MAKAIWAS SA MGA TECHNICAL ERRORS"
    },
    {
        "time": "22:00",
        "title": "10:00 PM REMINDER!",
        "type": "eservices_eod",
        "lines": "MAG EOD SA E-SERVICES.",
        "step1_title": "POS",
        "step1_sub": "REGULAR POS EOD",
        "step1_body": "Mag EOD sa POS tulad ng\nnakasanayan.",
        "step2_title": "E-SERVICES",
        "step2_sub": "E-SERVICES EOD",
        "step2_body": "Mag EOD sa E-Services.",
        "warning": "UGALIIN MAG EOD SA E-SERVICES\nMATAPOS ANG POS REGULAR EOD\nPARA MAKAIWAS SA MGA TECHNICAL ERRORS"
    }
]
