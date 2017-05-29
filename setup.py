from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()


version = '0.4.0'

install_requires = []


setup(name='energyplus_wrapper',
      version=version,
      description="some usefull function to run e+ with docker or locally",
      long_description=README,
      classifiers=[
          # Get strings from
          # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      ],
      keywords='energy-plus wrapper docker',
      author='Nicolas Cellier',
      author_email='contact@nicolas-cellier.net',
      url='https://github.com/celliern/energy_plus_wrapper/',
      license='DO WHAT THE FUCK YOU WANT TO',
      download_url='https://github.com/locie/energy_plus_wrapper/archive/v0.4.0.tar.gz',  # noqa: URL
      packages=find_packages('src'),
      package_dir={'': 'src'}, include_package_data=True,
      zip_safe=False,
      install_requires=install_requires
      )
