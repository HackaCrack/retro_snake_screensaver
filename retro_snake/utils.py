"""
Utility functions for Retro Snake Screensaver
"""

import ctypes
import atexit
import pygame

# Global flag to track if we've registered the atexit handler
_atexit_registered = False


def _emergency_cleanup():
    """Emergency cleanup function called at exit"""
    try:
        pygame.display.quit()
    except:
        pass
    try:
        pygame.quit()
    except:
        pass


def register_atexit_cleanup():
    """Register emergency cleanup handler (only once)"""
    global _atexit_registered
    if not _atexit_registered:
        atexit.register(_emergency_cleanup)
        _atexit_registered = True


def setup_dpi_awareness():
    """Enable DPI awareness on Windows to get correct screen resolution"""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def cleanup_pygame():
    """Ensure pygame is fully cleaned up"""
    try:
        pygame.display.quit()
    except:
        pass
    try:
        pygame.quit()
    except:
        pass

