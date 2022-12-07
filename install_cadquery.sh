# install this in the base environment
conda install conda-libmamba-solver

# create a new environment for tinyrace
conda create --name tinyrace
conda activate tinyrace
conda install -c cadquery -c conda-forge cq-editor=master black --experimental-solver=libmamba -v
