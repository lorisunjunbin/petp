"""
Debug helper for PyInstaller packaged applications.
This script should be used inside the packaged app to trace imports and file access.
"""

import os
import sys
import traceback
import logging
import importlib

# Configure logging
log_file = os.path.join('.', 'runtime_debug.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('PETP_Debug')

def log_system_info():
    """Log basic system information for diagnostics"""
    logger.info("=" * 80)
    logger.info("PETP Debug Runtime Starting")
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Executable: {sys.executable}")
    logger.info(f"Current Directory: {os.getcwd()}")
    logger.info(f"sys.path: {sys.path}")
    logger.info(f"OS Environment: {os.environ}")
    logger.info("=" * 80)

def test_critical_imports():
    """Test importing critical modules and log results"""
    critical_modules = [
        "wx", "numpy", "pandas", "PIL", "requests", "selenium", 
        "bs4", "sqlite3", "core.processors", "utils"
    ]
    
    for module in critical_modules:
        try:
            importlib.import_module(module)
            logger.info(f"Successfully imported: {module}")
        except Exception as e:
            logger.error(f"Failed to import {module}: {e}")
            logger.error(traceback.format_exc())

def verify_file_paths():
    """Verify critical file paths exist"""
    critical_paths = [
        "config",
        "core/executions",
        "core/processors",
        "image",
        "resources",
        "download"
    ]
    
    for path in critical_paths:
        # Try both relative and absolute paths
        abs_path = os.path.abspath(path)
        if os.path.exists(path):
            logger.info(f"Path exists (relative): {path}")
        elif os.path.exists(abs_path):
            logger.info(f"Path exists (absolute): {abs_path}")
        else:
            logger.error(f"Path does not exist: {path} | {abs_path}")
            
            # Check parent directory
            parent = os.path.dirname(abs_path)
            if os.path.exists(parent):
                logger.info(f"Parent directory exists: {parent}")
                logger.info(f"Contents: {os.listdir(parent)}")
            else:
                logger.error(f"Parent directory does not exist: {parent}")

def install_exception_hook():
    """Install global exception hook to log all uncaught exceptions"""
    original_hook = sys.excepthook
    
    def exception_hook(exc_type, exc_value, exc_traceback):
        logger.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))
        return original_hook(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = exception_hook

if __name__ == "__main__":
    # This section runs when executed directly, helpful for testing
    log_system_info()
    test_critical_imports()
    verify_file_paths()
    install_exception_hook()
else:
    # This section runs when imported, for use in the main application
    install_exception_hook()
    logger.info("Debug module loaded")

# Usage in main app:
# import debug_runtime  # At the top of your main script
