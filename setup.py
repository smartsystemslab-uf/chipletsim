# setup.py
# ============================================================
from setuptools import setup, find_packages

setup(
    name="chipletsim",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@institution.edu",
    description="Simulation framework for chiplet-based DNN accelerator design",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="git@github.com:smartsystemslab-uf/chipletsim.git",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.23",
        "pandas>=1.5",
        "matplotlib>=3.6",
        "seaborn>=0.12",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "pytest-cov", "jupyter"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
)
