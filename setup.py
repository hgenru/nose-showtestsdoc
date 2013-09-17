from setuptools import setup, find_packages

try:
    desc = open('README.rst').read()
except:
    desc = 'see README.rst'


setup(
    name="showtestsdoc",
    version="0.1",
    description="Nosetests plugin to show short tests docstring",
    long_description=desc,
    url="https://github.com/hgenru/nose-showtestsdoc",
    license="WTFPL",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['nose'],
    entry_points={
        'nose.plugins': ['showtestsdoc = showtestsdoc.showtestsdoc:TestsDoc']
    },

)