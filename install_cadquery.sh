# install this in the base environment
conda install conda-libmamba-solver

# create a new environment for tinyrace
conda create --name tinyrace2
conda activate tinyrace2
conda install -c cadquery -c conda-forge cq-editor=master --experimental-solver=libmamba -v
