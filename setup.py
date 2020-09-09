
import sys
import os


# Make sure we are running python3.5+
if 10 * sys.version_info[0] + sys.version_info[1] < 35:
    sys.exit("Sorry, only Python 3.5+ is supported.")


from setuptools import setup


def readme():
    print("Current dir = %s" % os.getcwd())
    print(os.listdir())
    with open('README.rst') as f:
        return f.read()

setup(
      name             =   'generate_hdf5',
      # for best practices make this version the same as the VERSION class variable
      # defined in your ChrisApp-derived Python class
      version          =   '0.1',
      description      =   'An app to convert original and segmented brain images in mgz format to .hdf5 format in axial, sagittall, and coronal plane',
      long_description =   readme(),
      author           =   'Sandip Samal',
      author_email     =   'sandip.samal@childrens.harvard.edu',
      url              =   'http://wiki',
      packages         =   ['generate_hdf5'],
      install_requires =   ['chrisapp', 'pudb'],
      test_suite       =   'nose.collector',
      tests_require    =   ['nose'],
      scripts          =   ['generate_hdf5/generate_hdf5.py'],
      license          =   'MIT',
      zip_safe         =   False
     )
