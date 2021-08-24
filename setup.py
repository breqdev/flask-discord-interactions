from setuptools import setup


with open("README.md") as file:
    readme = file.read()


setup(
    name='Flask-Discord-Interactions',
    version='1.0.5',
    url='https://github.com/Breq16/flask-discord-interactions',
    author='Brooke Chalmers',
    author_email='breq@breq.dev',
    description='A Flask extension for Discord slash commands.',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=['flask_discord_interactions'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        "Flask",
        "requests",
        "PyNaCl"
    ],
    extras_require={
        "async": ["Quart", "aiohttp"]
    },
    tests_require=["pytest"],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python',
    ],
    python_requires='>=3.7',
)
