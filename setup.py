import offlinesec-client
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='offlinesec-client',
    version=offlinesec-client.__version__,
    packages=find_packages(),
    url='https://offlinesec.com',
    author='Offline Security',
    author_email='info.offlinesec@gmail.com',
    description='Offline Security Client',
    long_description_content_type="text/markdown",
    long_description=long_description,
    entry_points={'console_scripts': ['offlinesec_sap_notes = offlinesec-client.req_notes_report:main',
                                      'offlinesec_get_reports = offlinesec-client.get_reports:main'], },
    install_requires=required,
    include_package_data=True
)
# packages=['offlinesec-client'],