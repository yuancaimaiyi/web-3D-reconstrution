import os
import sys
import sys
parent_path = os.path.dirname(sys.path[0])
if parent_path not in sys.path:
    sys.path.append(parent_path)
import numpy as np
import subprocess as sp
import argparse
import yaml
import struct
from log import Timer,LogWriter
import  sqlite3
import shutil
from pathlib import Path
import json
import re
from read_write_model import read_model
from tqdm import tqdm
from featuremanage import retrieval_pairs
from convertSfM import convert
import piexif
from PIL import Image
class VisMap:
    def __init__(self,images_path,fsba,pure_vision):
        ###########params
        self.dir =  Path(os.path.dirname(os.path.abspath(images_path)))
        self.vismap_path = "/app/hera-vismap/vismap/build/src/exe/colmap"
        self.images_path =  images_path
        self.folder_name =  os.path.split(images_path)[-1]
        self.sfm = self.dir / f'{self.folder_name}_sfm'
        os.makedirs(self.sfm,exist_ok=True)
        self.map = self.sfm / 'map'
        os.makedirs(self.map, exist_ok=True)
        self.tmp = self.sfm / 'tmp'
        os.makedirs(self.tmp, exist_ok=True)
        self.database_path = self.map / 'database.db'
        self.sparse_model = self.map / 'sparse_model'
        os.makedirs(self.sparse_model, exist_ok=True)
        self.database_path = self.map / 'database.db'
        self.GPU_IDX = 0
        self.multi_model = 0
        self.refine_focal = 1
        self.refine_principal = 0
        self.refine_distorted = 1
        self.gba_iterations = 30
        self.gba_refinements = 5
        self.resection_min_inliners =  30
        self.init_max_forward_motion = 1.0
        self.init_max_error = 4
        self.init_min_tri_angle = 5
        self.GPU_IDX = 0
        self.fsba = fsba
        self.pure_vision = pure_vision

        self.total_num = 0
        ############ 
        self.assign_cluster_id = 1
        self.write_binary = 0
        self.retriangulate = 0
        self.final_ba = 0
        self.num_images_ub = 500
        self.completeness_ratio = 0.8
        self.cluster_type = "NCUT"
        self.images_num = 0
        self.gpsInfoNum = 0
        for file in tqdm(os.listdir(self.images_path)):
            if file.endswith("jpg") or file.endswith("png"):
                img = Image.open(os.path.join(self.images_path,file))
                exif_dict = piexif.load(img.info['exif'])
                gpsInfo = exif_dict['GPS']
                if len(gpsInfo) !=0:
                    self.gpsInfoNum += 1
                self.images_num += 1
        if self.gpsInfoNum == 0 :
            self.pure_vision = 'true'
        print(f'#### params: \n')
        print(f'images num:{self.images_num}\n')
        print(f'cluster num: {self.num_images_ub}\n')
        print(f'global ba refinements: {self.gba_refinements}\n')
        print(f'whether use feature scale: {self.fsba}\n')
        print(f'whether pure vision : {self.pure_vision}\n')
        print(f'cluser type : {self.cluster_type}\n')
        self.log = LogWriter(self.map)
        self.log.heading(" VisMap SFM ")
    
    def read_next_bytes(self,fid, num_bytes, format_char_sequence, endian_character="<"):
        data = fid.read(num_bytes)
        return struct.unpack(endian_character + format_char_sequence, data)
    def read_images(self,path_to_model_file):
        num_reg_images = []
        if os.path.exists(os.path.join(path_to_model_file, "images.bin")):
            with open(os.path.join(path_to_model_file, "images.bin"), "rb") as fid:
                num_reg_images = self.read_next_bytes(fid, 8, "Q")[0]
            return num_reg_images, True
        elif os.path.exists(os.path.join(path_to_model_file, "images.txt")):
            with open(os.path.join(path_to_model_file, "images.txt"), "r+") as fid:
                for i, line in enumerate(fid.readlines()):
                    if i == 4:
                        num_reg_images = int(line.strip().split("#")[1])
                        break
            return num_reg_images, True
        else:
            return num_reg_images, False
    def dataInfo(self):
        db = sqlite3.connect(str(self.database_path))
        value = db.execute("SELECT name FROM IMAGES")
        name = []
        for n in value:
            name.append(n)
        self.total_num =len(name)
    def feature_extractor(self):
        timer = Timer()
        sp.call(["{}".format(self.vismap_path), "{}".format("feature_extractor"),
                 "--database_path","{}".format(self.database_path),
                 "--image_path","{}".format(self.images_path),
                 "--type","{}".format(0),
                 "--SiftExtraction.gpu_index","{}".format(self.GPU_IDX)])
        self.log.log("...feature extracting complete ({} sec)".format(timer.read()))
    def image_retrieval(self):
        sp.call(["{}".format(self.vismap_path), "{}".format("vocab_tree_retriever"),
                 "--database_path","{}".format(self.database_path),
                 "--vocab_tree_path","{}".format(self.vocab_path),
                 "--num_images","21",
                 "--output_path","{}".format(os.path.join(self.map,'retrieval.txt'))])
    def feature_matching(self):
        if self.images_num > 50:
            timer = Timer()
            retrieval_pairs.retrieval_pairs(self.images_path, self.map)
            
            if not os.path.exists(os.path.join(self.map,'global-feats-netvlad.txt')):
                print("retrieval's pairs not exit.....................")
                sys.exit(1)
            sp.call(["{}".format(self.vismap_path),"{}".format("vocab_tree_matcher"),
                            "--database_path","{}".format(self.database_path),
                            "--SiftMatching.guided_matching","{}".format(1),
                            "--VocabTreeMatching.match_list_path","{}".format(os.path.join(self.map,'global-feats-netvlad.txt')),
                            "--SiftMatching.gpu_index","{}".format(self.GPU_IDX)])
            self.log.log("...netvlad feature matching complete ({} sec)".format(timer.read()))
        else:
            timer = Timer()
            sp.call(["{}".format(self.vismap_path), "{}".format("exhaustive_matcher"),
                    "--database_path","{}".format(self.database_path),
                    "--SiftMatching.guided_matching", "{}".format(1),
                    "--SiftMatching.gpu_index","{}".format(self.GPU_IDX)])
            self.log.log("...sequential feature matching complete ({} sec)".format(timer.read()))           
    def array_to_blob(self,array):
        return array.tobytes()
    def mapper(self):
        timer = Timer()
        if  self.total_num < 500 :  
            self.num_images_ub = self.total_num
        map_mode = "distributed_mapper"
        sp.call(["{}".format(self.vismap_path), "{}".format(map_mode),
                "{}".format(self.tmp),
                "--database_path", "{}".format(self.database_path),
                "--image_path","{}".format(self.images_path),
                "--output_path", "{}".format(self.tmp),
                "--assign_cluster_id","{}".format(self.assign_cluster_id),
                "--write_binary","{}".format(self.write_binary),
                "--retriangulate","{}".format(self.retriangulate),
                "--final_ba","{}".format(self.final_ba),
                "--select_tracks_for_bundle_adjustment","{}".format(1),
                "--long_track_length_threshold","{}".format(10),
                "--graph_dir","{}".format(self.tmp),
                "--num_images_ub","{}".format(self.num_images_ub),
                "--completeness_ratio","{}".format(self.completeness_ratio),
                "--relax_ratio","{}".format(1.3),
                "--cluster_type","{}".format(self.cluster_type),
                "--Mapper.multiple_models", "{}".format(self.multi_model) ,
                "--Mapper.abs_pose_min_num_inliers","{}".format(self.resection_min_inliners),
                "--Mapper.ba_refine_focal_length","{}".format(self.refine_focal),
                "--Mapper.ba_refine_principal_point","{}".format(self.refine_principal),
                "--Mapper.ba_refine_extra_params","{}".format(self.refine_distorted),
                "--Mapper.ba_global_max_num_iterations","{}".format(self.gba_iterations),
                "--Mapper.ba_global_max_refinements","{}".format(self.gba_refinements),
                "--Mapper.init_max_forward_motion","{}".format(self.init_max_forward_motion),
                "--Mapper.init_max_error","{}".format(self.init_max_error),
                "--Mapper.init_min_tri_angle","{}".format(self.init_min_tri_angle),
                "--Mapper.all_use_feature_scale",self.fsba,
                "--Mapper.gba_use_feature_scale",self.fsba,
                "--image_overlap", "{}".format(100),
                # "--Mapper.tri_ignore_two_view_tracks", "0",
                "--Mapper.pure_vision", self.pure_vision])
        num_reg_images, label = self.read_images(os.path.join(self.tmp, "0"))
        print("...register {} success rate {}%".format(num_reg_images,num_reg_images * 100 / self.total_num))
        ## copy tmp to map
        for file in os.listdir(os.path.join(self.tmp,"0")):
            shutil.copy(os.path.join(os.path.join(self.tmp,"0"),file),os.path.join(self.sparse_model,file))
        self.log.log("... {} sfm complete ({} sec)".format(map_mode, timer.read()))
        convert(self.sparse_model,self.map/"reconstruction.json")
        print("convert colmap to json done ! \n")

images_path =  sys.argv[1]
fsba =  sys.argv[2]
pure_vision =  sys.argv[3]
vismap= VisMap(images_path , fsba , pure_vision )
vismap.feature_extractor()
vismap.feature_matching()
vismap.dataInfo()
vismap.mapper()
