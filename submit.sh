#!/bin/sh
# Grid Engine
#$ -N oFT_TSR4_noWaves
#$ -cwd
#$ -pe mpi 32 -R y
#$ -l h_vmem=4G
#$ -M callum.guy@ed.ac.uk
#$ -m beas
#$ -V

echo "Running job on $NSLOTS processors..."

# Initialise the environment modules
. /etc/profile.d/modules.sh

# Load OpenFOAM
module load openmpi
. /exports/applications/apps/community/eng/OpenFOAM-1912/OpenFOAM-v1912/etc/bashrc

# Load python
module load python

# Run the program
./runCase
