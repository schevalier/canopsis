from setuptools import setup, find_packages

install_requires = [
    "cstorage",
]

with open('README') as f:
    desc = f.read()

setup(
    name='ctopology',
    version='0.1',
    author="Capensis",
    author_email="canopsis@capensis.fr",
    description=("Store topology"),
    license="AGPL v3",
    zip_safe=False,
    keywords="ctopology storage store canopsis ctopology",
    install_requires=install_requires,
    url="http://www.canopsis.org",
    packages=find_packages(exclude='test'),
    scripts=['scripts/ctopology'],
    long_description=desc,
    test_suite="test"
)
