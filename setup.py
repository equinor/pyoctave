from setuptools import find_packages, setup

setup(
    name="pyoctave",
    description="simply python wrapper for octave",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    version="1.2.0",
    author="Equinor ASA",
    author_email="fg_gpl@equinor.com",
    license="LGPL-3.0",
    url="https://github.com/equinor/pyoctave",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries",
    ],
    include_package_data=True,
    install_requires=["scipy", "pexpect"],
    python_requires=">=3.6",
    tests_require=["pytest"],
)
