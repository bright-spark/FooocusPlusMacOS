import os
import sys
from pathlib import Path
from launch_support import is_win32_standalone_build

commit_id = ''
fooocusplus_ver = ''

def get_library_ver():
    if is_win32_standalone_build:
        current_library = Path('../python_embedded/embedded_version/library_version.py')
        if os.path.exists(current_library):
            embedded_version = os.path.abspath('../python_embedded/embedded_version')
            sys.path.append(embedded_version)
            from embedded_version import library_version
            return (library_version.version)
        else:
             return 0.96
    else:
        if os.path.exists('required_library.py'):
            import required_library
            return required_library.version
        else:
            return 1.00

def get_required_library():
    if (not os.path.exists('required_library.py')) or (not is_win32_standalone_build):
        return True
    import required_library
    if get_library_ver() >= (required_library.version):
        return True
    else:
        return False

def get_fooocusplus_ver():
    global fooocusplus_ver, commit_id
    if not fooocusplus_ver:
        fooocusplus_log = os.path.abspath(f'./fooocusplus_log.md')
        if os.path.exists(fooocusplus_log):
            with open(fooocusplus_log, "r", encoding="utf-8") as log_file:
                line = log_file.readline().strip()
                while line:
                    if line.startswith("# "):
                        break
                    line = log_file.readline().strip()
        else:
            line = '0.9.0'
        fooocusplus_ver = line.strip('# ')
        if commit_id:
            fooocusplus_ver += f'.{commit_id}'
    return fooocusplus_ver
