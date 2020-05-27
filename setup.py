# coding: utf-8

from pathlib import Path
from setuptools import setup, find_packages
from vpv import annotations
import os
import vpv

def get_annotation_files():
    """
    Need to find the non-.py file that are needed for annotations
    Returns
    -------

    """
    options_dir = Path(annotations.__file__).parent
    config_files = [os.path.relpath(x, Path(vpv.__file__).parent) for x in options_dir.rglob('*.yaml')]
    return config_files

# config_files = [x for x in options_dir.iterdir()]

setup(
    name='vpv_viewer',
    download_url='https://github.com/mpi2/lama/archive/0.9.4.tar.gz',
    version='2.2.4',
    packages=find_packages(exclude=("dev")),
	package_data={'': get_annotation_files()},  # Puts it in the wheel dist. MANIFEST.in gets it in source dist
    # package_data={'': ['current_commit',
    #                    'stats/rscripts/lmFast.R',
    #                    'stats/rscripts/r_padjust.R']},  # Puts it in the wheel dist. MANIFEST.in gets it in source dist
    include_package_data=True,
    install_requires=[
        'pyqt5',
        'simpleitk',
        'pyyaml',
        'scipy',
        'appdirs',
        'pillow',
        'lxml',
        'pyqtgraph',
        'toml',
        'python-dateutil'
    ],

    url='https://github.com/mpi2/vpv',
    license='Apache2',
    author='Neil Horner',
    author_email='n.horner@har.mrc.ac.uk, bit@har.mrc.ac.uk',
    description='Viewing and annotation of 3D volumetric phenotype data for the IMPC',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
     ],
    keywords=['image processing', 'bioinformatics', 'phenotype'],
    entry_points ={
            'console_scripts': [
                'vpv=vpv.run_vpv:main',
            ]
        },
)
