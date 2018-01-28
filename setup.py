#!/usr/bin/env python3

from distutils.core import setup

PYTHON_MODULES = [
    'ESSBackend', 'ESSBackend.app', 'ESSBackend.config', 'ESSBackend.init',
    'ESSBackend.models'
]

setup(
    name='ESS Backend',
    version='0.1',
    description='Environmental Sustainability Scorecard Backend',
    author='Daniel Theriault',
    packages=['ESSBackend'],
    # py_modules=PYTHON_MODULES,
    # entry_points={'console_scripts': ['ESSBackend = ESSBackend.app:main']},
)
