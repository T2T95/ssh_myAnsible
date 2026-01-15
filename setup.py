from setuptools import setup, find_packages

setup(
    name="mylittleansible",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mla = mylittleansible.cli:main',
        ],
    },
    install_requires=[
        'paramiko', 'jinja2', 'click', 'pyyaml'
    ],
)
