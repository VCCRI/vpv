# vpv
Volume Phenotype viewer. A desktop 3D volume viewer, for analysing results of automatic phenotype detection from the LAMA pipeline

Developed in Python using QT, and the superb [PyQtGraph](http://www.pyqtgraph.org/)

## Dependencies
* python3 => 3.6
* scipy
* PyQt5
* PyQtGraph


## Getting started
### On Linux

#### Get the VPV code
Either install git, then:
```bash
$ git clone https://github.com/mpi2/vpv.git
```

Or download the [source code](https://github.com/mpi2/vpv/archive/master.zip) and uzip

#### Install dependencies
```bash
# The following will install pipenv, which manages the dependencies
$ cd vpv/
$ ./setup_VPV.py
```

#### Running VPV
```bash
# Activate virual environment
$ cd vpv/
$ pipenv shell
$ ./vpv.py 
```

### On Windows
Download the latest Windows installer from [here](https://github.com/mpi2/vpv/releases/) 

Or get python3 ([For example Anaconda](https://www.anaconda.com/download/#windows) installed and follow instruction as for running on Linux above.

## Instructions
Drag and drop an image to overlay the stats onto (population average for example) and the t-statistics overlay
Make sure "Volume" is selected for the image and "Data" is selected for the overlay in the import dialog

![Import image](/vpv/docs/import_volume.png)

Take a look at the [vpv wiki](../../wiki)

## Authors ##
This software was developed by Neil Horner in the Bioimage Informatics Group at MRC Harwell UK (https://www.har.mrc.ac.uk) 
under the supervision of Henrik Westerberg.
 
If you have any questions or comments, please contact us at bit@har.mrc.ac.uk


## License
This project is licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0) - 
see the [LICENSE.md](/../LICENSE.md) file for details
