from setuptools import setup

setup(
    name='ESS Backend',
    version='0.1',
    description='Environmental Sustainability Scorecard Backend',
    author='Daniel Theriault',
    package_dir={'ESSbackend': '.'},
    packages=['ESSbackend'],
    entry_points={'console_scripts': ['ESSBackend = app:main']}, )
