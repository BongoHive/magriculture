from setuptools import setup, find_packages

def listify(filename):
    return filter(None, open(filename,'r').read().split('\n'))

setup(
    name = "magriculture",
    version = "0.1.0",
    url = 'http://github.com/praekelt/magriculture',
    license = '?',
    description = "Tool to provide market information to "
                  "smallholding farmers in emerging markets.",
    long_description = open('README','r').read(),
    author = 'Praekelt Foundation',
    author_email = 'dev@praekeltfoundation.org',
    packages = find_packages(),
    install_requires = ['setuptools'].extend(listify('config/requirements.pip')),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Private Developers',
        'License :: ? :: ?',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking'
    ]
)

