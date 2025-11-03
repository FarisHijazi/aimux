"""Setup script for uzi."""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='uzi',
    version='0.1.0',
    description='AI coding agent orchestration tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Uzi Team',
    url='https://github.com/devflowinc/uzi',
    packages=find_packages(),
    python_requires='>=3.11',
    install_requires=[
        'pyyaml>=6.0',
    ],
    entry_points={
        'console_scripts': [
            'uzi=uzi.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
