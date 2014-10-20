--[[

module load gcc python/2.7.8

pip install --install-option="--prefix=/home/idhmc/apps/beautifulsoup4/4.3.2" --verbose beautifulsoup4==4.3.2

]]

local prefix = "/home/idhmc/apps/beautifulsoup4/4.3.2"
local pythonpath = pathJoin(prefix, "lib/python2.7/site-packages")

prereq('python')

prepend_path("PYTHONPATH", pythonpath)
