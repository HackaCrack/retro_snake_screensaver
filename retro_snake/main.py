"""
Main entry point for Retro Snake Screensaver
"""

import sys
import os
from retro_snake.config import load_config
from retro_snake.screensaver import ScreenSaver, capture_desktop_screenshot
from retro_snake.ui import ConfigDialog
from retro_snake.preview import PreviewWindow, run_fallback_preview, HAS_WIN32, acquire_preview_mutex
from retro_snake.utils import register_atexit_cleanup, cleanup_pygame, setup_dpi_awareness


def parse_windows_args():
    """Parse Windows screensaver command line arguments"""
    # Windows passes args like /s, /c, /p:12345
    # Sometimes with : sometimes without
    
    if len(sys.argv) < 2:
        return 'screensaver', None  # Default: run screensaver
    
    arg = sys.argv[1].lower().strip()
    
    # Handle /s or -s (screensaver mode)
    if arg in ['/s', '-s', '--screensaver']:
        return 'screensaver', None
    
    # Handle /c or -c (configure)
    if arg.startswith('/c') or arg.startswith('-c') or arg == '--configure':
        return 'configure', None
    
    # Handle /p or -p (preview)
    if arg.startswith('/p') or arg.startswith('-p') or arg == '--preview':
        # Try to get window handle
        hwnd = None
        if ':' in arg:
            try:
                hwnd = int(arg.split(':')[1])
            except ValueError:
                pass
        elif len(sys.argv) > 2:
            try:
                hwnd = int(sys.argv[2])
            except ValueError:
                pass
        return 'preview', hwnd
    
    # Handle -w or --windowed (for testing)
    if arg in ['-w', '--windowed']:
        return 'windowed', None
    
    return 'screensaver', None


def main():
    """Entry point with Windows screensaver argument support"""
    # Setup DPI awareness
    setup_dpi_awareness()
    # Register emergency cleanup handler
    register_atexit_cleanup()
    
    mode, hwnd = parse_windows_args()
    
    try:
        if mode == 'configure':
            # Show configuration dialog
            dialog = ConfigDialog()
            result = dialog.run()
            
            if result == 'preview':
                # Run preview after config
                load_config()
                screensaver = ScreenSaver(windowed=True)
                screensaver.run()
        
        elif mode == 'preview':
            # Preview mode - embed in Windows screensaver preview window
            # Check for existing preview instance BEFORE any initialization
            mutex_handle, acquired = acquire_preview_mutex()
            if not acquired:
                # Another preview instance is already running, exit immediately
                os._exit(0)
            
            load_config()
            
            try:
                if hwnd and HAS_WIN32:
                    # Proper embedded preview using Windows API
                    try:
                        preview = PreviewWindow(hwnd, mutex_handle)
                        preview.run()
                    except Exception as e:
                        # Fallback to simple preview window
                        run_fallback_preview()
                else:
                    # Fallback: No hwnd or Windows API unavailable - show standalone small window
                    run_fallback_preview()
            finally:
                # Release mutex when preview exits
                try:
                    from retro_snake.preview import release_preview_mutex
                    release_preview_mutex(mutex_handle)
                except:
                    pass
        
        elif mode == 'windowed':
            # Windowed mode for testing
            config = load_config()
            # Capture desktop screenshot BEFORE pygame init if transparent mode is enabled
            desktop_screenshot = None
            if config.get('transparent_mode', False):
                desktop_screenshot = capture_desktop_screenshot()
            screensaver = ScreenSaver(windowed=True, desktop_screenshot=desktop_screenshot)
            screensaver.run()
        
        else:  # screensaver mode
            config = load_config()
            # Capture desktop screenshot BEFORE pygame init if transparent mode is enabled
            desktop_screenshot = None
            if config.get('transparent_mode', False):
                desktop_screenshot = capture_desktop_screenshot()
            screensaver = ScreenSaver(windowed=False, desktop_screenshot=desktop_screenshot)
            screensaver.run()
    
    except Exception as e:
        pass  # Silently handle errors
    finally:
        # Ensure pygame is cleaned up no matter what
        cleanup_pygame()
        # Force immediate process termination - os._exit bypasses all handlers
        os._exit(0)


if __name__ == "__main__":
    main()

