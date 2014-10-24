load("gcc/4.8.2")
load("python/2.7.8")
load("beautifulsoup4") --local
load("leptonica/1.71")
load("icu/52.1")
--load("tesseract/3.03-rc1")
load("tesseract/3.02-r889")
load("java/1.7.0_67")

local emop_home = os.getenv("EMOP_HOME")

pushenv("JUXTA_HOME", pathJoin(emop_home, "lib/juxta-cl"))
pushenv("RETAS_HOME", pathJoin(emop_home, "lib/retas"))
pushenv("SEASR_HOME", pathJoin(emop_home, "lib/seasr"))
pushenv("TESSDATA_PREFIX", "/dh/data/shared/")
pushenv("DENOISE_HOME", pathJoin(emop_home, "lib/denoise"))
