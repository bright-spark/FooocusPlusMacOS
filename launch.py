import os
import ssl
import sys
import enhanced.version as version
from pathlib import Path
from common import ROOT

print('[System ARGV] ' + str(sys.argv))
print(f'Root {ROOT}')
sys.path.append(ROOT)
os.chdir(ROOT)

if not version.get_required_library():
    print()
    print('Our apologies for the inconvenience, but the installed')
    print(f'Python library does not support FooocusPlus {version.get_fooocusplus_ver()}')
    print('Please install the new python_embedded archive from')
    print('https://huggingface.co/DavidDragonsage/FooocusPlus/')
    print()
    quit()

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
os.environ["translators_default_region"] = "China"
if "GRADIO_SERVER_PORT" not in os.environ:
    os.environ["GRADIO_SERVER_PORT"] = "7865"
ssl._create_default_https_context = ssl._create_unverified_context

from modules.launch_util import is_installed, verify_installed_version,\
    run, python, run_pip, run_pip_url, requirements_met,\
    git_clone, index_url, target_path_install, met_diff

torch_ver = ""
torchruntime_ver = '1.16.1'
verify_installed_version('torchruntime', torchruntime_ver)

import torchruntime
import platform
import comfy.comfy_version

from launch_support import build_launcher, delete_torch_dependencies, dependency_resolver, \
is_win32_standalone_build, python_embedded_path, \
read_torch_base, write_torch_base
from modules.model_loader import load_file_from_url


def prepare_environment():
    global torch_ver
    REINSTALL_ALL = False
    target_path_win = Path(python_embedded_path/'Lib/site-packages')
    requirements_file = os.environ.get('REQS_FILE', "requirements_versions.txt")
    torch_dict = dependency_resolver()
    torch_ver = torch_dict['torch_ver']
    torchvision_ver = torch_dict['torchvision_ver']
    torchaudio_ver = torch_dict['torchaudio_ver']
    xformers_ver = torch_dict['xformers_ver']
    pytorchlightning_ver = torch_dict['pytorchlightning_ver']
    lightningfabric_ver = torch_dict['lightningfabric_ver']
    torch_base_ver = read_torch_base()

    print(f"Python {sys.version}")
    print(f"Python Library {version.get_library_ver()}, Comfy version: {comfy.comfy_version.version}")
    print(f"Torch base version: {torch_base_ver}")
    print(f"FooocusPlus version: {version.get_fooocusplus_ver()}")
    print()
    print('Checking for required library files and loading Xformers...')

    # ensure urllib is available before it is needed
    verify_installed_version('urllib3', '2.4.0', False)

    if REINSTALL_ALL or torch_ver != torch_base_ver:
        print(f'Using Torchruntime to configure Torch')
        print(f'Updating to Torch {torch_ver} and its dependencies:')
        print(torch_dict)
        print()
        delete_torch_dependencies()

        if sys.platform == "darwin":  # macOS
            # For macOS, use CPU-only PyTorch
            run_pip('install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu', 'Installing PyTorch for macOS')
        elif torch_ver == "2.7.0":  # NVIDIA 50xx support
            run_pip_url('install torch torchaudio torchvision', 'NVIDIA 50xx support', 'https://download.pytorch.org/whl/cu128')
        else:
            # For other platforms, use standard installation
            run_pip(f'install torch=={torch_ver} torchvision=={torchvision_ver} torchaudio=={torchaudio_ver}', 'Installing PyTorch')
        
        verify_installed_version('pytorch-lightning', pytorchlightning_ver, False)
        verify_installed_version('lightning-fabric', lightningfabric_ver, False)


    if REINSTALL_ALL or not is_installed("xformers"):
        if sys.platform == "darwin":
            # Skip xformers on macOS as it's not well supported
            print("Skipping xformers installation on macOS as it's not well supported.")
            print("The application will run without xformers optimization.")
        elif platform.python_version().startswith("3.10"):
            xformers_statement = "xformers==" + xformers_ver
            torchruntime.install(["--no-deps", xformers_statement])
        else:
            print("Installation of xformers is not supported in this version of Python.")
            print("You can also check this and build manually:" +\
                "https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Xformers#building-xformers-on-windows-by-duckness")
            if not is_installed("xformers"):
                print("Continuing without xformers...")

    if REINSTALL_ALL or not requirements_met(requirements_file):
        if len(met_diff.keys())>0:
            for p in met_diff.keys():
                print(f'Uninstall {p}.{met_diff[p]} ...')
                run(f'"{python}" -m pip uninstall -y {p}=={met_diff[p]}')
        if is_win32_standalone_build:
            run_pip(f"install -r \"{requirements_file}\" -t {target_path_win}", "requirements")
        else:
            run_pip(f"install -r \"{requirements_file}\"", "requirements")

    patch_requirements = "requirements_patch.txt"
    if (REINSTALL_ALL or not requirements_met(patch_requirements)) and not\
        is_win32_standalone_build:
            print('Updating with required patch files...')
            run_pip(f"install -r \"{patch_requirements}\"", "patching requirements")
    return


vae_approx_filenames = [
    ('xlvaeapp.pth', 'https://huggingface.co/lllyasviel/misc/resolve/main/xlvaeapp.pth'),
    ('vaeapp_sd15.pth', 'https://huggingface.co/lllyasviel/misc/resolve/main/vaeapp_sd15.pt'),
    ('xl-to-v1_interposer-v4.0.safetensors',
     'https://huggingface.co/mashb1t/misc/resolve/main/xl-to-v1_interposer-v4.0.safetensors')
]


def ini_args():
    from args_manager import args
    return args

prepare_environment()
build_launcher()
args = ini_args()

if args.gpu_device_id is not None:
    os.environ['CUDA_VISIBLE_DEVICES'] = str(args.gpu_device_id)
    print("Set device to:", args.gpu_device_id)

if args.hf_mirror is not None:
    os.environ['HF_MIRROR'] = str(args.hf_mirror)
    print("Set hf_mirror to:", args.hf_mirror)


import modules.preset_resource as PR
from modules import config
from modules.hash_cache import init_cache
from modules.meta_parser import parse_meta_from_preset
from modules.user_structure import empty_dir
from ldm_patched.modules.model_management import get_vram
os.environ["U2NET_HOME"] = config.paths_inpaint[0]
os.environ["BERT_HOME"] = config.paths_llms[0]
os.environ['GRADIO_TEMP_DIR'] = config.temp_path

write_torch_base(torch_ver)

if config.temp_path_cleanup_on_launch:
    print(f'Attempting to cleanup the temporary directory: {config.temp_path}')
    result = empty_dir(config.temp_path)
    if result:
        print("Cleanup successful")
    else:
        print(f"Failed to cleanup the content of the temp. directory")


launch_vram = int(get_vram()/1000)
if launch_vram<6:
    print()
    print(f'The video card has only {launch_vram}GB of memory (VRAM) but FooocusPlus')
    print('will give you access to models that are optimized for Low VRAM systems.')
    print('However, any system with less than 6GB of VRAM will tend to be slow')
    print('and unreliable, and may or may not be able to generate Flux images.')
    print('Some 4GB VRAM cards may even be unable to generate SDXL images.')

    if launch_vram<4: # some folks actually can run Flux with 4GB VRAM cards, so only lock out those with less than that
        print()
        if args.language == 'cn':
            print(f'系统GPU显存容量太小，无法正常运行Flux, SD3, Kolors和HyDiT等最新模型，将自动禁用Comfyd引擎。请知晓，尽早升级硬件。')
        else:
            print('Systems with less than 4GB of VRAM are not be able to run large models such as Flux, SD3, Kolors and HyDiT.')
        args.async_cuda_allocation = False
        args.disable_async_cuda_allocation = True
        args.disable_comfyd = True
    print()


def download_models(default_model, previous_default_models, checkpoint_downloads, embeddings_downloads, lora_downloads, vae_downloads):
    from modules.util import get_file_from_folder_list

    for file_name, url in vae_approx_filenames:
        load_file_from_url(url=url, model_dir=config.path_vae_approx, file_name=file_name)

    load_file_from_url(
        url='https://huggingface.co/lllyasviel/misc/resolve/main/fooocus_expansion.bin',
        model_dir=config.path_fooocus_expansion,
        file_name='pytorch_model.bin'
    )

    if args.disable_preset_download:
        print('Skipped model download.')
        return default_model, checkpoint_downloads

    if not args.always_download_new_model:
        if not os.path.isfile(get_file_from_folder_list(default_model, config.paths_checkpoints)):
            for alternative_model_name in previous_default_models:
                if os.path.isfile(get_file_from_folder_list(alternative_model_name, config.paths_checkpoints)):
                    print(f'You do not have [{default_model}] but you have [{alternative_model_name}].')
                    print(f'FooocusPlus will use [{alternative_model_name}] to avoid downloading new models.')
                    print('Use --always-download-new-model to avoid fallback and always get new models.')
                    checkpoint_downloads = {}
                    default_model = alternative_model_name
                    break

    for file_name, url in checkpoint_downloads.items():
        model_dir = os.path.dirname(get_file_from_folder_list(file_name, config.paths_checkpoints))
        load_file_from_url(url=url, model_dir=model_dir, file_name=file_name)

    for file_name, url in embeddings_downloads.items():
        load_file_from_url(url=url, model_dir=config.path_embeddings, file_name=file_name)

    for file_name, url in lora_downloads.items():
        model_dir = os.path.dirname(get_file_from_folder_list(file_name, config.paths_loras))
        load_file_from_url(url=url, model_dir=model_dir, file_name=file_name)

    for file_name, url in vae_downloads.items():
        load_file_from_url(url=url, model_dir=config.path_vae, file_name=file_name)

    return default_model, checkpoint_downloads

if (config.default_low_vram_presets or launch_vram<6) and \
    (PR.current_preset == 'initial' or PR.current_preset == 'Default'):
    low_vram_preset = PR.get_lowVRAM_preset_content()
    if low_vram_preset != '':
        preset_prepared = parse_meta_from_preset(low_vram_preset)
        if config.default_comfyd_active_checkbox:
            comfyd.stop()
        default_model = preset_prepared.get('base_model')
        config.default_base_model_name = default_model
        config.default_cfg_scale = preset_prepared.get('guidance_scale')
        config.default_overwrite_step = preset_prepared.get('steps')
        config.default_sample_sharpness = preset_prepared.get('sharpness')
        previous_default_models = preset_prepared.get('previous_default_models', [])
        checkpoint_downloads = preset_prepared.get('checkpoint_downloads', {})
        embeddings_downloads = preset_prepared.get('embeddings_downloads', {})
        lora_downloads = preset_prepared.get('lora_downloads', {})
        vae_downloads = preset_prepared.get('vae_downloads', {})


config.default_base_model_name, config.checkpoint_downloads = download_models(
    config.default_base_model_name, config.previous_default_models, config.checkpoint_downloads,
    config.embeddings_downloads, config.lora_downloads, config.vae_downloads)

config.update_files()
init_cache(config.model_filenames, config.paths_checkpoints, config.lora_filenames, config.paths_loras)

from webui import *
