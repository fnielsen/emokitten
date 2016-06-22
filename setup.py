"""Installation and setup configuration."""


from setuptools import setup


setup(
    name='emokitten',
    description="Installation and setup configuration",
    py_modules=['emokitten'],
    entry_points={
        'console_scripts': [
            'emokitten = emokitten:main',
        ],
    },
)
