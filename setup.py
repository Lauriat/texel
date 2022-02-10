from setuptools import setup

requirements = [
    "openpyxl",
    "odfpy",
    "pyperclip",
    "numpy",
]

with open("README.md") as f:
    long_description = f.read()

setup(
    name="texel",
    packages=["texel"],
    version="0.2.1",
    description="Command line interface for reading spreadsheets inside terminal.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    python_requires=">=3",
    entry_points={"console_scripts": ["texel = texel.texel:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    author="Lauri Tuominen",
    author_email="lauri.a.tuominen@gmail.com",
    url="https://github.com/lauriat/texel",
)
