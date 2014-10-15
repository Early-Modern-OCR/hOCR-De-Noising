--[[

module load gcc python

pip install --user --verbose beautifulsoup4==4.3.2

]]

local home = os.getenv("HOME")
local prefix = pathJoin(home, ".local")
local pythonpath = pathJoin(prefix, "lib/python2.7/site-packages")

prereq('python')

prepend_path("PYTHONPATH", prefix)
