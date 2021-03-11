import os
import re
import setuptools

with open(os.path.join("configurator", "__init__.py"), encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setuptools.setup(
    name="configurator",
    version=version,
    author="Zeke Marffy",
    author_email="zmarffy@yahoo.com",
    packages=setuptools.find_packages(),
    url='https://github.com/zmarffy/configurator',
    license='',
    description='library to help change INI files',
    python_requires='>=3.7',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[  
        'str2bool'
    ],
)
