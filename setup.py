from setuptools import setup, find_packages

setup(
    name = "svgmap",
    version = "0.1.0",
    author = "Nat Wilson",
    author_email = "natw@fortyninemaps.com",
    description = "GeoJSON to SVG converter",
    license = "MIT",
    packages = find_packages(),
    install_requires = ["picogeojson"],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
