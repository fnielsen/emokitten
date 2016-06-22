"""Installation and setup configuration."""


from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='emokitten',
    description="Installation and setup configuration",
    install_requires=requirements,
    py_modules=['emokitten'],
    entry_points={
        'console_scripts': [
            'emokitten = emokitten:main',
        ],
    },
)
