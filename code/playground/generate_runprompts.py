import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Input folder path")
parser.add_argument("-r", "--runner", help="runner folder")
parser.add_argument("-f", "--folder", help="Input folder path")
parser.add_argument("-o", "--output", help="Output folder")
parser.add_argument("-t", "--tag", help="Tag")
args = parser.parse_args()


template = """#!/bin/bash

#SBATCH --job-name={param1}_{param2}
#SBATCH --output={param1}_{param2}_%j.out
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=6G
#SBATCH --gres=gpu:4
#SBATCH --exclude=cn01


echo "Job Started!"

apptainer run --nv --bind /home/kardosp/shared/data:/hdd /home/kardosp/envs/huggingface_env.sif python3 /home/kardosp/kgmatch/runprompts_accelerate.py -f /hdd/{param3} -fi {param4} -o /hdd/{param5} -m meta-llama/Llama-3.1-70B-Instruct

echo "Job Finished at $(date)!"
"""

if not os.path.exists(args.runner):
    os.makedirs(args.runner)

for file in os.listdir(args.input):

    with open(os.path.join(args.runner, file.replace(".json", ".sbatch")),"w") as f:
        f.write(template.format(param1=args.tag, param2=file.replace(".json", ""), param3=args.folder, param4=file, param5=args.output))