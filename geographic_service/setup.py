from distutils.core import setup

setup(
    name = 'geographic',
    version = '1.1',
    packages = ['geographic'],
    install_requires = ['osmnx', 'googlemaps'],
)