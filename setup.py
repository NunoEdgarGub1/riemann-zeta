from setuptools import setup, find_packages

setup(
    name='riemann-zeta',
    version='0.0.1',
    author='James Prestwich',
    license='NONE',
    packages=find_packages(),
    package_dir={'zeta': 'zeta'},
    install_requires=[
        'connectrum'
    ],
    tests_require=[
        'tox',
        'mypy',
        'flake8',
        'pytest',
        'pytest-cov'
    ],
    python_requires='>=3.6'
)
