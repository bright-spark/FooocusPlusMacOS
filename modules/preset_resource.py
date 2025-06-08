import os
import json
import random
import gradio as gr
import args_manager
import modules.aspect_ratios as AR
from ldm_patched.modules import model_management
from pathlib import Path

current_preset = args_manager.args.preset

# set by modules.config
default_bar_category = 'Favorite'
preset_bar_length = 8

# set by modules.config
# updated by modules.meta_parser.parse_meta_from_preset(preset_content)
refiner_switch = 0.6
default_sampler = 'dpmpp_2m_sde_gpu'

def find_preset_file(preset):
    if os.path.splitext(preset)[1] == 'json':
        preset_json = preset
    else:
        preset_json = f'{preset}.json'
    preset_file = ''
    preset_path = Path('presets')
    for preset_file in preset_path.rglob(preset_json):
        if preset_file.exists():
            AR.preset_file = str(preset_file)  # used to guarantee use of SD1.5 AR template
            return str(preset_file)
    print(f'Could not find the {preset} preset')
    print()
    return ''

def find_preset_category(preset):
    global preset_file
    preset_file = find_preset_file(preset)
    preset_category = os.path.basename(os.path.dirname(preset_file))
    return preset_category

category_selection = find_preset_category(current_preset)

def get_preset_paths():              # called by update_files() in modules.config
    preset_path = Path('presets')    # also used to check if preset files exist
    presets = list(preset_path.rglob('*.json'))
    if not presets:
        print('No presets found')
        return ['initial']
    return [str(p) for p in presets]  # Convert Path objects to strings

def get_random_preset_and_category():
    presets = get_preset_paths()
    random_index = random.randint(0, (len(presets)-1))
    file_path = presets[random_index]
    random_category = os.path.basename(os.path.dirname(file_path))
    file_path = Path(file_path)
    random_preset = file_path.stem
    print()
    print(f'Selected the {random_preset} preset at random')
    print(f'{random_preset} is in the {random_category} category')
    return random_category, random_preset

def get_presets_in_folder(arg_folder_name):
    if not arg_folder_name:
        arg_folder_name = category_selection
    if arg_folder_name == '.\presets':
        arg_folder_name = ''
    presets_in_folder = []
    if os.path.basename(os.path.dirname(arg_folder_name)) == 'presets':
        folder_name = Path(arg_folder_name)
    else:
        folder_name = Path(f'.\presets\{arg_folder_name}')
    if os.path.exists(folder_name):
        presets_in_folder = list(folder_name.rglob('*.json'))
        if not presets_in_folder:
            print(f'Could not find presets in the {arg_folder_name} folder.')
            print()
    else:
        print(f'Could not find the {arg_folder_name} folder.')
        print()
    return presets_in_folder

def get_presetnames_in_folder(folder_name):
    presetnames_in_folder = []
    if folder_name == 'All':
        folder_name = '.\presets'
    presets_in_folder = get_presets_in_folder(folder_name)
    if presets_in_folder:
        for preset_file in presets_in_folder:
            presetname = Path(preset_file)
            presetnames_in_folder.append(presetname.stem)
        if folder_name == '.\presets': # if we are listing files in all folders
            temp_set = set(presetnames_in_folder)    # then remove duplicates
            presetnames_in_folder = sorted(temp_set) # now convert back to a list
    return presetnames_in_folder

def get_all_presetnames():
    return get_presetnames_in_folder('.\presets')

def set_category_selection(arg_category_selection):
    global category_selection
    if arg_category_selection == '':
        category_selection = 'Favorite'
    category_selection = arg_category_selection
    if category_selection == 'Random':
        category_selection, preset_value = get_random_preset_and_category()
        preset_choices = get_presetnames_in_folder(category_selection)
    else:
        preset_choices = get_presetnames_in_folder(category_selection)
        if current_preset in preset_choices:
            preset_value = current_preset
        else:
            preset_value = preset_choices[0]
    return gr.update(value=category_selection),\
        gr.update(choices=preset_choices, value=preset_value),\
        gr.update(value=f'Current Preset: {current_preset}')

def set_preset_selection(arg_preset_selection, state_params):
    global current_preset, default_sampler
    if arg_preset_selection == '':
        if current_preset == '':
            current_preset = args_manager.args.preset
        print(f'Using the {current_preset} preset...')
    elif current_preset != arg_preset_selection:
        current_preset = arg_preset_selection  # update the current preset tracker
    state_params.update({'bar_button': current_preset})
    AR.current_preset = current_preset # for use by AR Shortlist/Standard toggle
    return gr.update(value=current_preset), \
        gr.update(value=state_params), \
        gr.update(value=f'Current Preset: {current_preset}'), \
        gr.update(value=AR.current_AR), \
        gr.update(value=default_sampler)

def bar_button_change(bar_button, state_params):
    global category_selection, current_preset
    state_params.update({'bar_button': bar_button})
    current_preset = bar_button
    category_selection = find_preset_category(current_preset)
    return state_params, gr.update(value=category_selection),\
        gr.update(value=current_preset)

def get_preset_content(preset):
    preset_file = find_preset_file(preset)
    if preset_file:
        try:
          with open(preset_file, "r", encoding="utf-8") as json_file:
              json_content = json.load(json_file)
              print(f'Loaded the {preset} preset content from {preset_file}')
              return json_content
        except Exception as e:
            print(f'Could not load the {preset} preset content from {preset_file}')
            print(e)
        print()
    return {}

def get_initial_preset_content():
    global current_preset, category_selection, default_bar_category
    json_content = ''
    preset = args_manager.args.preset
    if not find_preset_file(preset):
        if find_preset_file('Default'):
            preset = 'Default'
        else:
            print('Could not find the startup preset')
            category_selection = 'Random'
            if not preset:
                print('Could not find any presets')
                current_preset = 'initial'
    if category_selection != 'Random' and current_preset != 'initial':
        args_manager.args.preset = preset
        current_preset = preset
        category_selection = find_preset_category(preset)
    if current_preset != 'initial':
        set_category_selection(category_selection)
        json_content = get_preset_content(current_preset)
    return json_content

def get_lowVRAM_preset_content():
    global current_preset, category_selection, default_bar_category
    json_content = ''
    if find_preset_file('4GB_Default'):
        AR.low_vram = True
        category_selection = 'LowVRAM'
        default_bar_category = category_selection
        args_manager.args.preset = '4GB_Default'
        current_preset = args_manager.args.preset
        json_content = get_preset_content(current_preset)
        print('The 4GB_Default preset is optimized for low VRAM systems')
    return json_content


def get_preset_foldernames():
    preset_folder = '.\presets'
    preset_foldernames = []
    if os.path.exists(preset_folder):
        preset_foldernames = [f.name for f in os.scandir(preset_folder) if f.is_dir()]
        if not preset_foldernames:
            print(f'Could not find any preset subfolders in {preset_folder}')
            print()
            return preset_foldernames
    else:
        print(f'Could not find the {preset_folder} folder')
        print()
    return preset_foldernames

def get_preset_categories():
    preset_categories = get_preset_foldernames()
    if preset_categories:
        preset_categories.append('All')
        preset_categories.append('Random')
        preset_categories.sort()
    return preset_categories

def preset_count():
    return len(get_preset_paths())

def pad_list(arg_list, arg_length, arg_value):
    list_length = len(arg_list)
    if list_length >= arg_length:
        return arg_list
    else:
        padding_size = arg_length - list_length
        padded_list = arg_list + [arg_value] * padding_size
        return padded_list

def preset_bar_count():
    global default_bar_category
    preset_bar_list = get_presets_in_folder(default_bar_category)
    preset_bar_count = len(preset_bar_list)
    return preset_bar_count

def save_preset(x):
    global category_selection, current_preset
    PR_choices = get_presetnames_in_folder(category_selection)
    return gr.update(), gr.update(value=current_preset), \
        gr.update(choices=PR_choices)
