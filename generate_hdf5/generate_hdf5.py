#!/usr/bin/env python                                            
#
# generate_hdf5 ds ChRIS plugin app
#
# (c) 2016-2019 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#


import os
import sys
import time
import glob
import h5py
import numpy as np
import nibabel as nib
from data_loader.load_neuroimaging_data import map_aparc_aseg2label, create_weight_mask, transform_sagittal, \
                                               transform_axial, get_thick_slices, filter_blank_slices_thick


sys.path.append(os.path.dirname(__file__))

# import the Chris app superclass
from chrisapp.base import ChrisApp


Gstr_title = """
                                 _         _         _  __ _____ 
                                | |       | |       | |/ _|  ___|
  __ _  ___ _ __   ___ _ __ __ _| |_ ___  | |__   __| | |_|___ \ 
 / _` |/ _ \ '_ \ / _ \ '__/ _` | __/ _ \ | '_ \ / _` |  _|   \ \
| (_| |  __/ | | |  __/ | | (_| | ||  __/ | | | | (_| | | /\__/ /
 \__, |\___|_| |_|\___|_|  \__,_|\__\___| |_| |_|\__,_|_| \____/ 
  __/ |                               ______                     
 |___/                               |______|                    


"""

Gstr_synopsis = """

(Edit this in-line help for app specifics. At a minimum, the 
flags below are supported -- in the case of DS apps, both
positional arguments <inputDir> and <outputDir>; for FS apps
only <outputDir> -- and similarly for <in> <out> directories
where necessary.)

    NAME

       generate_hdf5.py 

    SYNOPSIS

        python generate_hdf5.py                                         \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--man]                                                     \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [-v <level>] [--verbosity <level>]                          \\
            [--version]                                                 \\
            <inputDir>                                                  \\
            <outputDir> 

    BRIEF EXAMPLE

        * Bare bones execution

            mkdir in out && chmod 777 out
            python generate_hdf5.py   \\
                                in    out

    DESCRIPTION

        `generate_hdf5.py` ...

    ARGS

        [-h] [--help]
        If specified, show help message and exit.
        
        [--json]
        If specified, show json representation of app and exit.
        
        [--man]
        If specified, print (this) man page and exit.

        [--meta]
        If specified, print plugin meta data and exit.
        
        [--savejson <DIR>] 
        If specified, save json representation file to DIR and exit. 
        
        [-v <level>] [--verbosity <level>]
        Verbosity level for app. Not used currently.
        
        [--version]
        If specified, print version number and exit. 

"""


class Generate_hdf5(ChrisApp):
    """
    An app to convert original and segmented brain images in mgz format to .hdf5 format in axial, sagittall, and coronal plane.
    """
    AUTHORS                 = 'Sandip Samal (sandip.samal@childrens.harvard.edu)'
    SELFPATH                = os.path.dirname(os.path.abspath(__file__))
    SELFEXEC                = os.path.basename(__file__)
    EXECSHELL               = 'python3'
    TITLE                   = 'A training data set generation app'
    CATEGORY                = ''
    TYPE                    = 'ds'
    DESCRIPTION             = 'An app to convert original and segmented brain images in mgz format to .hdf5 format in axial, sagittal, and coronal plane'
    DOCUMENTATION           = 'http://wiki'
    VERSION                 = '0.1'
    ICON                    = '' # url of an icon image
    LICENSE                 = 'Opensource (MIT)'
    MAX_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MAX_CPU_LIMIT           = '' # Override with millicore value as string, e.g. '2000m'
    MIN_CPU_LIMIT           = '' # Override with millicore value as string, e.g. '2000m'
    MAX_MEMORY_LIMIT        = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT        = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_GPU_LIMIT           = 0  # Override with the minimum number of GPUs, as an integer, for your plugin
    MAX_GPU_LIMIT           = 0  # Override with the maximum number of GPUs, as an integer, for your plugin

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """
        # Training settings

        self.add_argument('--hdf5_name', dest='dataset_name',type=str,optional = True, default="testsuite_2.hdf5",
                        help='path and name of hdf5-dataset (default: testsuite_2.hdf5)')
        self.add_argument('--plane',dest='plane', type=str, default="axial",optional = True, choices=["axial", "coronal", "sagittal"],
                        help="Which plane to put into file (axial (default), coronal or sagittal)")
        self.add_argument('--height',dest='height', type=int,optional = True, default=256, help='Height of Image (Default 256)')
        self.add_argument('--width', dest = 'height', type=int,optional = True, default=256, help='Width of Image (Default 256)')
        self.add_argument('--thickness',dest = 'slice_thickness',type=int,optional = True, default=3, help="Number of pre- and succeeding slices (default: 3)")
        self.add_argument('--pattern',dest ='pattern', type=str,optional = True, help="Pattern to match files in directory.",default="")
        self.add_argument('--image_name',dest='image_name', type=str,optional = True, default="mri/orig.mgz",
                        help="Default name of original images. FreeSurfer orig.mgz is default (mri/orig.mgz)")
        self.add_argument('--gt_name',dest = 'gt_name', type=str,optional = True, default="mri/aparc.DKTatlas+aseg.mgz",
                        help="Default name for ground truth segmentations. Default: mri/aparc.DKTatlas+aseg.mgz."
                             " If Corpus Callosum segmentation is already removed, do not set gt_nocc."
                             " (e.g. for our internal training set mri/aparc.DKTatlas+aseg.filled.mgz exists already"
                             " and should be used here instead of mri/aparc.DKTatlas+aseg.mgz). ")


        
    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        print(Gstr_title)
        print('Version: %s' % self.get_version())
        
        self.search_pattern = os.path.join(options.inputdir, options.pattern)
        self.subject_dirs = os.listdir(self.search_pattern)
        print (self.subject_dirs)
        self.data_set_size = len(self.subject_dirs)
        self.create_hdf5_dataset(options,plane=options.plane)

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)
    def create_hdf5_dataset( self,options,plane='axial', is_small=False):
        """
        Function to store all images in a given directory (or pattern) in a hdf5-file.
        :param str plane: which plane is processed (coronal, axial or saggital)
        :param bool is_small: small hdf5-file for pretraining?
        :return:
        """
        start_d = time.time()

        # Prepare arrays to hold the data
        orig_dataset = np.ndarray(shape=(256, 256, 0, 2 * options.slice_thickness + 1), dtype=np.uint8)
        aseg_dataset = np.ndarray(shape=(256, 256, 0), dtype=np.uint8)
        weight_dataset = np.ndarray(shape=(256, 256, 0), dtype=np.float)
        subjects = []

        # Loop over all subjects and load orig, aseg and create the weights
        for idx, current_subject in enumerate(self.subject_dirs):

            try:
                start = time.time()

                print("Volume Nr: {} Processing MRI Data from {}/{}".format(idx, current_subject, options.image_name))

                # Load orig and aseg
                orig = nib.load(os.path.join(options.inputdir,current_subject, options.image_name))
                orig = np.asarray(orig.get_fdata(), dtype=np.uint8)

                aseg = nib.load(os.path.join(options.inputdir,current_subject, options.gt_name))

                print('Processing ground truth segmentation {}'.format(options.gt_name))
                aseg = np.asarray(aseg.get_fdata(), dtype=np.int32)
               
                
                # Map aseg to label space and create weight masks
                if plane == 'sagittal':
                    _, mapped_aseg = map_aparc_aseg2label(aseg, aseg_nocc)
                    weights = create_weight_mask(mapped_aseg)
                    orig = transform_sagittal(orig)
                    mapped_aseg = transform_sagittal(mapped_aseg)
                    weights = transform_sagittal(weights)

                else:
                    mapped_aseg, _ = map_aparc_aseg2label(aseg)
                    weights = create_weight_mask(mapped_aseg)
                
                # Transform Data as needed (swap axis for axial view)
                if plane == 'axial':
                    orig = transform_axial(orig)
                    mapped_aseg = transform_axial(mapped_aseg)
                    weights = transform_axial(weights)

                # Create Thick Slices, filter out blanks
                orig_thick = get_thick_slices(orig, options.slice_thickness)
                orig, mapped_aseg, weights = filter_blank_slices_thick(orig_thick, mapped_aseg, weights)

                # Append finally processed images to arrays
                orig_dataset = np.append(orig_dataset, orig, axis=2)
                aseg_dataset = np.append(aseg_dataset, mapped_aseg, axis=2)
                weight_dataset = np.append(weight_dataset, weights, axis=2)

                sub_name = current_subject.split("/")[-1]
                subjects.append(sub_name.encode("ascii", "ignore"))

                end = time.time() - start

                print("Volume: {} Finished Data Reading and Appending in {:.3f} seconds.".format(idx, end))

                if is_small and idx == 2:
                    break

            except Exception as e:
                print("Volume: {} Failed Reading Data. Error: {}".format(idx, e))
                continue

        # Transpose to N, H, W, C and expand_dims for image

        orig_dataset = np.transpose(orig_dataset, (2, 0, 1, 3))
        aseg_dataset = np.transpose(aseg_dataset, (2, 0, 1))
        weight_dataset = np.transpose(weight_dataset, (2, 0, 1))

        # Write the hdf5 file
        with h5py.File(options.dataset_name, "w") as hf:
            hf.create_dataset('orig_dataset', data=orig_dataset, compression='gzip')
            hf.create_dataset('aseg_dataset', data=aseg_dataset, compression='gzip')
            hf.create_dataset('weight_dataset', data=weight_dataset, compression='gzip')

            dt = h5py.special_dtype(vlen=str)
            hf.create_dataset("subject", data=subjects, dtype=dt, compression="gzip")

        end_d = time.time() - start_d
        print("Successfully written {} in {:.3f} seconds.".format(options.outputdir + "/"+options.dataset_name, end_d))

# ENTRYPOINT
if __name__ == "__main__":
    chris_app = Generate_hdf5()
    chris_app.launch()
