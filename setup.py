from setuptools import setup, find_packages

def listify(filename):
    return filter(None, open(filename,'r').read().split('\n'))

def remove_externals(requirements):
    return filter(lambda e: not e.startswith('-e'), requirements)

setup(
    name = "magriculture",
    version = "0.1.0",
    url = 'http://github.com/praekelt/magriculture',
    license = '?',
    description = "Tool to provide market information to "
                  "smallholding farmers in emerging markets.",
    long_description = open('README.rst','r').read(),
    author = 'Praekelt Foundation',
    author_email = 'dev@praekeltfoundation.org',
    packages = find_packages(),
    install_requires = ['setuptools'] +
        remove_externals(listify('config/requirements.pip')),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Private Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking'
    ]
)

