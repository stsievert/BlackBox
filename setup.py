from setuptools import setup, find_packages

setup(name='blackbox',
      version='0.1.2',
      description='A flight recorder for scientific experiments.',
      url='http://github.com/lalitkumarj/blackbox',
      author='Lalit Jain and Scott Sievert',
      author_email='lalitkumarj@gmail.com',
      packages=find_packages(),
      install_requires=
      [
          'ujson',
          'msgpack-python',
          'msgpack_numpy'
      ])
      
