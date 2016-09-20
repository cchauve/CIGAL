from distutils.core import setup
from cigal.config import VERSION

setup(name="cigal",
      version=VERSION,
      url="http://cgl.bioinfo.uqam.ca",
      maintainer="Yannick Gingras",
      maintainer_email="ygingras@ygingras.net",
      packages=["cigal"],
      scripts=["bin/cigal", "bin/cigalgui"],
      license="GPL",
      summary="compute and display connection intervals for two genomes",
      # TODO: add the licence for those fonts
      data_files=[('share/ttf', ['ttf/FreeSans.ttf',
                                 'ttf/FreeSansBold.ttf'])]
      )
