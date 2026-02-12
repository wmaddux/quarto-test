# rules/__init__.py
__version__ = "1.6.0"

# Map your specific filenames to the report's expected import names
from . import service_error_skew_check as error_skew_check
from . import version_consistency_check
from . import network_acceleration_check
from . import storage_deadlock_check as deadlock_check
from . import sindex_on_flash_check as sindex_check
from . import sprig_limit_check as sprigs_check
from . import hwm_check
from . import memory_hwm_check
from . import config_symmetry_check
from . import config_drift_check
from . import hot_key_check
from . import read_not_found_check
from . import delete_not_found_check
from . import set_object_skew_check
from . import capacity_check