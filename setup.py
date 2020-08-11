from setuptools import setup

markdown = open('README.md',mode='r')
requirements = open('requirements.txt', mode='r')

setup(name='ShellCreator',
    version='0.4.2',
    description='A library to create command line interfaces.',
    long_description=markdown.read(),
    long_description_content_type='text/markdown',
    url='https://github.com/mewais/ShellCreator',
    author='Mohammad Ewais',
    author_email='mewais@ece.utoronto.ca',
    license='MIT',
    packages=['ShellCreator', 'ShellCreator.Utils'],
    install_requires=[list(filter(None, requirements.read().split('\n')))],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ])

requirements.close()
markdown.close()
