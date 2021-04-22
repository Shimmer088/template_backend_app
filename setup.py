import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simple-backend-app",
    version="0.0.1",
    author="Shimmer088",
    author_email="sfbaui@uzanet.ru",
    description="A small example backend app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
