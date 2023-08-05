import sys
import os
import time
from pathlib import Path

# Absolute path of this file
dirname = os.path.dirname(os.path.abspath(__file__))


def create_dir(path):
    try:
        os.mkdir(path)
    except:
        pass


def run(bin_path, mg_path, img_path, additional_parameters):
    print(bin_path, mg_path, img_path, additional_parameters)

    bin_path = Path(bin_path)
    mg_path = Path(mg_path)
    img_path = Path(img_path)

    sensor_database = bin_path / 'aliceVision' / 'share' / 'aliceVision' / 'cameraSensors.db'
    tree = bin_path / 'aliceVision' / 'share' / 'aliceVision' / 'vlfeat_K80L3.SIFT.tree'

    create_dir(img_path / 'result')

    cmd = "{} ".format(bin_path / 'meshroom_batch') + \
          "--input {} ".format(img_path) + \
          "--cache {} ".format(img_path / 'cache') + \
          "--pipeline {} ".format(mg_path) + \
          "--paramOverrides CameraInit.sensorDatabase={} ImageMatching.tree={} ".format(sensor_database, tree) + \
          "--output {} ".format(img_path / 'result') + \
          " ".join(additional_parameters)

    print(cmd)
    os.system(cmd)


def main():
    # Path of the Meshroom's binary files
    bin_path = sys.argv[1]
    # Path of the pipeline graph
    mg_path = sys.argv[2]
    # Path of an folder with images
    img_path = sys.argv[3]
    # Extra meshroom_batch parameters
    additional_parameters = sys.argv[4:]

    start_time = time.time()

    run(bin_path, mg_path, img_path, additional_parameters)

    end_time = time.time()
    hours, rem = divmod(end_time-start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print("time elapsed: "+"{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))


main()
