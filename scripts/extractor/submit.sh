#!/bin/sh

#PBS -P darpa.ml.cse
#PBS -q high
#PBS -lselect=1:ncpus=1:ngpus=1:centos=skylake
#PBS -lwalltime=01:00:00

echo "==============================="
echo $PBS_JOBID
cat $PBS_NODEFILE
echo $PBS_JOBNAME
echo "==============================="

source /home/apps/anaconda3_2018/4.6.9/etc/profile.d/conda.sh
conda activate ~/plan
cd /home/cse/dual/cs5180404/scratch/JEEAdv-GPT4/scripts/extractor/

./train_extractor.sh
