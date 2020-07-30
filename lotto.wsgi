import os, sys
import logging
logging.basicConfig(stream=sys.stderr)
if not ("/var/www/lotto" in sys.path):
        sys.path.insert(0,"/var/www/lotto")
from lotto import app as application
