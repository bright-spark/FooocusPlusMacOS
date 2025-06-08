import os
import sys
from common import ROOT

path_root = ROOT

def init_module(file_path):
    module_root = os.path.dirname(file_path)
    sys.path.append(module_root)
    module_name = os.path.relpath(module_root, os.path.dirname(os.path.abspath(__file__)))
    if module_name == "OneButtonPrompt":
        print(f'[{module_name}] The Random Prompt custom module is initializing...')
    else:
        print(f'[{module_name}] The {module_name} custom module is initializing...')
    return module_name, module_root
