import subprocess
import os
import yaml
import sys

ROOT = subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')
sys.path.append(os.path.join(ROOT, 'src'))
from utils import AerialImage

# initialize
config_path = os.path.join(ROOT, 'config', 'ensemble_config.yaml')
image_path = os.path.join(ROOT, 'data', 'P0000.jpg')
bfp_path = os.path.join(ROOT, 'data', 'P0000.json')

with open(config_path, 'r') as f:
    conf = yaml.load(f, Loader=yaml.FullLoader)
    
class ensembleTree:
    def __init__(self, image_path, bfp_path, model_weights_path, device):
        self.ROOT_DIR = os.path.dirname(os.path.realpath('__file__'))
        self.TEST_MODE = 'inference'
        self.DEVICE = device  # "/gpu:0" if conf['SCORING']['GPU_DEVICE'] else  '/cpu:0'
        self.weights = model_weights_path
        self.image_path = image_path
        _, self.file_extension = os.path.splitext(self.image_path)
        self.bfp_path = bfp_path
        self.num_masks = 0

    def calc_ratio(self, pred_mask, padding_pct):
        self.img_prj_path = AerialImage().georeferencing(self.bfp_path, self.image_path, padding_pct)
        raster = rio.open(self.img_prj_path)
        bfp = gpd.read_file(self.bfp_path)
        im_array = AerialImage().extract_image(raster, bfp)
        h, w = im_arry.shape[:2]
        img_area = h * w

        # total roof
        r, g, b = im_array[0, :, :], im_array[1, :, :], im_array[2, :, :]
        r[r > 0] = 1
        g[g > 0] = 1
        b[b > 0] = 1
        roof = (r + g + b)
        roof[roof > 0] = 1
        tot_roof = roof.sum()
        pct_roof = round(tot_roof / img_area * 100, 2)

        return [img_area, tot_roof, pct_roof]


def score():
    
    device = "/gpu:0" if conf['SCORING']['GPU_DEVICE'] else '/cpu:0'
    ent = ensembleTree(image_path, bfp_path, conf['SCORING']['MODEL_WEIGHTS'], device)


    img_metrics = ent.calc_ratio(None, conf['SCORING']['BUILDING_FOOTPRINT_PADDING'])
    ratio_names = ['img_area', 'tot_roof', 'pct_roof']

    return dict(zip(ratio_names, img_metrics))
