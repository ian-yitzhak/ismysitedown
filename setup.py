from setuptools import setup, find_packages

setup(
    name="website-checker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["Django>=4.0", "requests>=2.25.0"],
    entry_points={"console_scripts": ["website-checker=website_checker.cli:main"]},
    include_package_data=True,
)