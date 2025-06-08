import os
import glob
from pathlib import Path
import platform
import shutil
import sys
import args_manager


win32_root = (Path.cwd()).parent
python_embedded_path = Path(win32_root/'python_embedded')
is_win32_standalone_build = python_embedded_path.is_dir()

torch_base_ver = ''
win32_cmd = '''
@echo off
.\python_embedded\python.exe -s FooocusPlus\{cmds} %*
pause
'''

def build_launcher():
    if not is_win32_standalone_build:
        return

    branches = {"FooocusPlus": "entry_with_update.py", "FooocusPlus_dev": "entry_with_update.py --dev",\
        "FooocusPlus_without_update": "launch.py", "FooocusPlus_commit": "launch_with_commit.py 56e5200"}

    for (name, cmd) in branches.items():
        win32_cmd_preset = win32_cmd.replace('{cmds}', f'{cmd}')
        bat_path = os.path.join(win32_root, f'run_{name}.bat')
        if not os.path.exists(bat_path) or name=='FooocusPlus_commit':
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(win32_cmd_preset)
    return


def dependency_resolver():
    """
    Provides the dependent versions of a Torch build.
    Returns a dictionary with:
    - torch_ver: str
    - torchvision_ver: str
    - torchaudio_ver: str
    - xformers_ver: str
    - pytorchlightning_ver: str
    - lightningfabric_ver: str
    """
    # Set versions compatible with macOS
    if sys.platform == "darwin":  # macOS
        torch_default = "2.1.0"
        torchvision_default = "0.16.0"
        torchaudio_default = "2.1.0"
        xformers_default = "0.0.22.post4"  # Last version with pre-built wheels for macOS
        pytorchlightning_default = "2.2.0"
        lightningfabric_default = "2.2.0"
    else:
        # Default versions for other platforms
        torch_default = "2.1.0"
        torchvision_default = "0.16.0"
        torchaudio_default = "2.1.0"
        xformers_default = "0.0.22.post4"
        pytorchlightning_default = "2.2.0"
        lightningfabric_default = "2.2.0"

    torch_ver = torch_default # initialize torch to the default

    import torchruntime
    from torchruntime.device_db import get_gpus
    from torchruntime.platform_detection import get_torch_platform
    # from torchruntime.platform_detection import get_nvidia_arch #new coding

    gpus = get_gpus()
    torchruntime_platform = get_torch_platform(gpus)


    # First, take care of special cases
    # Note, torchruntime/torchruntime/platform_detection.py
    # suggests "directml" should be used for Intel
    #
    if platform.machine == "amd64" or torchruntime_platform == "xpu":
        args_manager.directml = True # switch on AMD/Intel support
        torch_ver = "2.3.1"

    # Detection Logic: Windows (win32) defaults to "2.5.1", unless "cu128"
    if (sys.platform == "win32") and (torchruntime_platform == "nightly/cu128"):
        torch_ver = "2.7.0"

    elif sys.platform == "linux": # Linux also defaults to "2.5.1"
        if torchruntime_platform == "nightly/cu128":
            torch_ver = "2.7.0"
        elif torchruntime_platform == "rocm5.7":
            torch_ver = "2.3.1"
        elif torchruntime_platform == "rocm5.2":
            torch_ver = "1.13.1"

    elif sys.platform == "darwin": # (OSX) Apple Silicon defaults to "2.5.1"
        if platform.machine == "amd64":
            torch_ver = "2.2.2"

    # Begin the assignment of dependencies:
    if torch_ver == "2.7.0": # NVIDIA 50xx support
        dependencies = dict(
            torch_ver = "2.7.0",
            torchvision_ver = "0.22.0",
            torchaudio_ver = "2.7.0",
            xformers_ver = xformers_default,
            pytorchlightning_ver = pytorchlightning_default,
            lightningfabric_ver = lightningfabric_default,
        )

    elif torch_ver == "2.4.1":
        dependencies = dict(
            torch_ver = "2.4.1",
            torchvision_ver = "0.19.1",
            torchaudio_ver = "2.4.1",
            xformers_ver = "0.0.28.post1",
            pytorchlightning_ver = "2.5.1.post0", # will be compatible with slightly older versions
            lightningfabric_ver = "2.5.1",
        )

    elif torch_ver == "2.3.1": # for Linux rocm5.7
        dependencies = dict(
            torch_ver = "2.3.1",
            torchvision_ver = "0.18.1",
            torchaudio_ver = "2.3.1",
            xformers_ver = "0.0.27",
            pytorchlightning_ver = "2.4.0",
            lightningfabric_ver = "2.4.0",
        )

    elif torch_ver == "2.2.2": # last version supporting Intel Macs
        dependencies = dict(
            torch_ver = "2.2.2",
            torchvision_ver = "0.17.2",
            torchaudio_ver = "2.2.2",
            xformers_ver = "0.0.27.post2", # but not MPS compatible
            pytorchlightning_ver = "2.4.0", # confirm 2.5.1 compatibility when versioning policy updated
            lightningfabric_ver = "2.4.0",
        )

    elif torch_ver == "1.13.1": # earliest possible supported release: rocm5.2
        dependencies = dict(
            torch_ver = "1.13.1",
            torchvision_ver = "0.14.1",
            torchaudio_ver = "0.13.1",
            xformers_ver = "0.0.20", # but not compatible with ROCm, rocm6.2.4 only
            pytorchlightning_ver = "2.2.5",
            lightningfabric_ver = "2.2.5",
        )

    else:
        # use the defaults
        dependencies = dict(
            torch_ver = torch_default,
            torchvision_ver = torchvision_default,
            torchaudio_ver = torchaudio_default,
            xformers_ver = xformers_default,
            pytorchlightning_ver = pytorchlightning_default,
            lightningfabric_ver = lightningfabric_default,
        )

    # return the result
    return dependencies

def delete_torch_dependencies():
    if is_win32_standalone_build:
        library_path = os.path.abspath(f'../python_embedded/Lib/site-packages')
        file_paths = ['torch', 'torchaudio', 'torchvision', 'xformers',\
            'pytorch_lightning', 'lightning-fabric']
        for file_path in file_paths:
            scratch_path = file_path
            if os.path.exists(f'{library_path}/{file_path}'):
                print(file_path)
                shutil.rmtree(f'{library_path}/{file_path}', ignore_errors=True)
            for scratch_path in glob.glob(f'{library_path}/{file_path}-*-info'):
                print(scratch_path)
                shutil.rmtree(scratch_path, ignore_errors=True)
    return

def get_split_value(full_string):
    divider = '= '
    scratch = full_string.split(divider, 1)
    split_value = scratch[1] if len(scratch) > 1 else ''
    return split_value


def get_torch_base_path(): # this ignores config.txt settings
    if args_manager.args.user_dir:
        torch_base_path = os.path.abspath(args_manager.args.user_dir)
    else:
        torch_base_path = os.path.abspath(os.path.join(os.pardir, 'UserDir/torch_base.txt'))
    return torch_base_path

def read_torch_base(): #this ignores config.txt settings
    global torch_base_path
    torch_base_path = get_torch_base_path()
    try:
        torch_base = open(torch_base_path, 'r')
        torch_base_ver = torch_base.readline().strip()
        torch_base_ver = get_split_value(torch_base_ver)
        torch_base.close()
    except:
        torch_base_ver = 'not found'
        return torch_base_ver
    if torch_base_ver == '':
       torch_base_ver = 'needs to be installed'
    else:
       torch_base_ver = read_torch_user_base()
    return torch_base_ver

def read_torch_user_base(): #this uses config.txt settings
    if is_win32_standalone_build:
        if not os.path.exists(os.path.abspath(f'../python_embedded/Lib/site-packages/torch')):
            return 'not installed'
    from modules.config import user_dir
    try:
        torch_base_path2 = os.path.abspath(f'{user_dir}/torch_base.txt')
        torch_base = open(torch_base_path2, 'r')
        torch_base_ver = torch_base.readline().strip()
        torch_base_ver = get_split_value(torch_base_ver)
        torch_base.close()
    except:
        torch_base_ver = 'undefined'
    return torch_base_ver

def write_torch_base(torch_base_ver):
    global torch_base_path
    torch_base = open(torch_base_path, "w")
    torch_base.write(f"Torch base version = {torch_base_ver}")
    torch_base.close()
    from modules.config import user_dir
    torch_base_path2 = os.path.abspath(f'{user_dir}/torch_base.txt')
    if torch_base_path2 == torch_base_path:
        return
    torch_base = open(torch_base_path, "w")
    torch_base.write(f"Torch base version = {torch_base_ver}")
    torch_base.close()
    return
