# eMOP Controller

The Brazos Cluster controller process for the eMOP workflow.

## Build

Step #1 is specific to the Brazos cluster and can be skipped if you have maven available.

1. Load maven module.

        module use ./modulefiles
        module load emop-build

2. Build and install all necessary dependencies.

        make

## Setup

Depends on several environment variables as well. They are:

* TESSDATA_PREFIX - Path to the Tesseract training data
* JUXTA_HOME - Root directory for JuxtaCL
* RETAS_HOME - Root directory for RETAS
* SEASR_HOME - Root directory for SEASR post-processing tools
* DENOISE_HOME - Root directory for the DeNoise post-processing tool

For multiple users to run this controller on the same file structure the umask must be set to at least 002.

Add the following to your login scripts such as ~/.bashrc

    umask 002

The file `config.ini` contains all the configuration options used by the emop-controller.

## Running

TODO

## Support

The use of this application relies heavily on sites using the following technologies

* SLURM - cluster resource manager
* Lmod - Modules environment

Only the following versions of each dependency have been tested.

* python-2.7.8
* maven-3.2.1
* java-1.7.0-67
* tesseract - SVN revision 889

See `modulefiles/emop.lua` and `modulefiles/emop-build.lua` for a list of all the applications used
