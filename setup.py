from setuptools import setup

setup(
    name="texel",
    packages=["texel"],
    entry_points={"console_scripts": ["texel = texel.texel:main"]},
    version="0.0.1",
    description="Spreadsheet cli",
    author="Lauri Tuominen",
    author_email="lauri.a.tuominen@gmail.com",
)
