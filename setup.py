import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='bigcommerce',
    version='0.0.12',
    author='John LeBlanc',
    author_email='johnleblanciii@gmail.com',
    description='Bigcommerce Endpoints',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/LeBlanciii/bigcommerce',
    project_urls={
    },
    license='MIT',
    packages=['bigcommerce'],
    install_requires=['requests'],
)
