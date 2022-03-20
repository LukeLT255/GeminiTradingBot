from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: MacOS',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='gemini',
    version='0.0.1',
    description="Modules for working with Gemini's API ina pythonic way",
    long_description="",
    url='',
    author='Luke Tyson',
    author_email='LukeLT25@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='gemini',
    packages=find_packages(),
    install_requires=[open('requirements.txt').read()]

)