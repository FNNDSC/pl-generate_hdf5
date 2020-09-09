pl-generate_hdf5
================================

.. image:: https://badge.fury.io/py/generate_hdf5.svg
    :target: https://badge.fury.io/py/generate_hdf5

.. image:: https://travis-ci.org/FNNDSC/generate_hdf5.svg?branch=master
    :target: https://travis-ci.org/FNNDSC/generate_hdf5

.. image:: https://img.shields.io/badge/python-3.5%2B-blue.svg
    :target: https://badge.fury.io/py/pl-generate_hdf5

.. contents:: Table of Contents


Abstract
--------

An app to convert original and segmented brain images in mgz format to .hdf5 format in axial, sagittall, and coronal plane


Synopsis
--------

.. code::

    python generate_hdf5.py                                           \
        [-v <level>] [--verbosity <level>]                          \
        [--version]                                                 \
        [--man]                                                     \
        [--meta]                                                    \
        <inputDir>
        <outputDir> 

Description
-----------

``generate_hdf5.py`` is a ChRIS-based application that...

Arguments
---------

.. code::

    [-v <level>] [--verbosity <level>]
    Verbosity level for app. Not used currently.

    [--version]
    If specified, print version number. 
    
    [--man]
    If specified, print (this) man page.

    [--meta]
    If specified, print plugin meta data.


Run
----

This ``plugin`` can be run in two modes: natively as a python package or as a containerized docker image.

Using PyPI
~~~~~~~~~~

To run from PyPI, simply do a 

.. code:: bash

    pip install generate_hdf5

and run with

.. code:: bash

    generate_hdf5.py --man /tmp /tmp

to get inline help. The app should also understand being called with only two positional arguments

.. code:: bash

    generate_hdf5.py /some/input/directory /destination/directory


Using ``docker run``
~~~~~~~~~~~~~~~~~~~~

To run using ``docker``, be sure to assign an "input" directory to ``/incoming`` and an output directory to ``/outgoing``. *Make sure that the* ``$(pwd)/out`` *directory is world writable!*

Now, prefix all calls with 

.. code:: bash

    docker run --rm -v $(pwd)/out:/outgoing                             \
            fnndsc/pl-generate_hdf5 generate_hdf5.py                        \

Thus, getting inline help is:

.. code:: bash

    mkdir in out && chmod 777 out
    docker run --rm -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
            fnndsc/pl-generate_hdf5 generate_hdf5.py                        \
            --man                                                       \
            /incoming /outgoing

Examples
--------





