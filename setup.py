from setuptools import setup

requirements = [
    "pandas",
    "pyperclip",
    "numpy",
]

with open("README.md") as f:
    long_description = f.read()

setup(
    name="texel",
    packages=["texel"],
    version="0.0.1",
    description="Command line interface for reading spreadsheets inside terminal.",
    long_description=long_description,
    install_requires=requirements,
    entry_points={"console_scripts": ["texel = texel.texel:main"]},
    licence="MIT",
    author="Lauri Tuominen",
    author_email="lauri.a.tuominen@gmail.com",
    url="https://github.com/lauriat/texel",
)
