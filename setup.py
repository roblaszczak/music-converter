from setuptools import setup, find_packages

setup(name='music-converter',
      version='0.1',
      description='Music converter',
      author='Robert Laszczak',
      author_email='eventched@gmail.com',
      packages=find_packages(exclude=['tests']),
      scripts=['scripts/music-converter'])
