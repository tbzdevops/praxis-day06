from setuptools import setup, find_packages

setup(
    name='flaskapp',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Flask>=3.1,<4'
    ],
    entry_points={
        'console_scripts': [
            'run-flask=app.main:main'
        ]
    }
)
