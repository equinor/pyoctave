from setuptools import find_packages, setup

setup(
    name="pyoctave",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    test_suite="tests",
    install_requires=[],
    tests_require=["pytest"],
)
