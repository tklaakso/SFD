from distutils.core import setup

setup(
    name = 'geographic',
    version = '1.4',
    packages = ['geographic'],
    install_requires = ['osmnx', 'googlemaps'],
)