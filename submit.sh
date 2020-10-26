#!/bin/sh
# Grid Engine
#$ -N olaFlowTurbine_Mesh_Ind_ExEx_Fine
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

# Run the program
./runCase
