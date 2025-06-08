import os
import common
from backend_base import backend_base, utils, comfyd, torch_version, xformers_version, cuda_version, comfyclient_pipeline
from backend_base.params_mapper import ComfyTaskParams
from backend_base.models_info import ModelsInfo, sync_model_info

args_comfyd = [[]]
modelsinfo_filename = 'models_info.json'

def init_modelsinfo(models_root, path_map):
    global modelsinfo_filename
    models_info_path = os.path.abspath(os.path.join(models_root, modelsinfo_filename))
    if not common.MODELS_INFO:
        common.MODELS_INFO = ModelsInfo(models_info_path, path_map)
    return common.MODELS_INFO
