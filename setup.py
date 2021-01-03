"""
Flask-Discord-Interactions

A Flask extension to enable function-based definitions for Discord slash
commands.
"""
from setuptools import setup


setup(
    name='Flask-Discord-Interactions',
    version='0.1.0',
    url='https://github.com/Breq16/flask-discord-interactions',
    author='Wesley Chalmers',
    author_email='breq@breq.dev',
    description='A Flask extension for Discord slash commands.',
    long_description=__doc__,
    py_modules=['flask_discord_interactions'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        "Flask",
        "requests",
        "PyNaCl"
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python',
    ],
    python_requires='>=3.8',
)
