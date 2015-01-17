load("gcc/4.8.2")
load("python/2.7.8")
load("beautifulsoup4") --local
load("leptonica/1.71")
load("icu/52.1")
--load("tesseract/3.03-rc1")
load("tesseract/3.02-r889")
load("java/1.7.0_67")

if (mode() == "load") then
  if (not os.getenv("EMOP_HOME")) then
    local cwd = lfs.currentdir()
    LmodMessage("WARNING: EMOP_HOME is not set, setting to ", cwd)
    setenv("EMOP_HOME", cwd)
  end
end

local emop_home = os.getenv("EMOP_HOME")
setenv("JUXTA_HOME", pathJoin(emop_home, "lib/juxta-cl"))
setenv("RETAS_HOME", pathJoin(emop_home, "lib/retas"))
setenv("SEASR_HOME", pathJoin(emop_home, "lib/seasr"))
setenv("TESSDATA_PREFIX", "/dh/data/shared/")
setenv("DENOISE_HOME", pathJoin(emop_home, "lib/denoise"))
