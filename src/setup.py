from setuptools import setup

setup(
    name='ESS Backend',
    version='0.1',
    description='Environmental Sustainability Scorecard Backend',
    author='Daniel Theriault',
    package_dir={'ESSBackend': '.'},
    packages=['ESSBackend'],
    entry_points={'console_scripts': ['ESSBackend = ESSBackend.app:main']}, )
