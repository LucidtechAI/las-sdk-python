from setuptools import setup

with open('requirements.txt') as fp:
    install_requires = fp.readlines()


with open('README.md') as fp:
    readme = fp.read()


setup(
    name='lucidtech-las',
    version='3.2.6',
    description='Python SDK for Lucidtech AI Services',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='Apache 2.0',
    platforms='Posix; MacOS X; Windows',
    author='Lucidtech',
    maintainer='August Kvernmo',
    maintainer_email='august@lucidtech.ai',
    url='https://github.com/LucidtechAI/las-sdk-python',
    packages=['las'],
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet'
    ]
)
