from setuptools import setup, find_packages

with open('./requirements.txt') as reqs:
    requirements = [line.rstrip() for line in reqs]

setup(name="cognition_datasources",
      version='0.1',
      author='Jeff Albrecht',
      author_email='geospatialjeff@gmail.com',
      packages=find_packages(exclude=['tests', 'datasources/static/cbers/cbers_reference.geojson', 'datasources/static/naip/coverages', 'docs']),
      install_requires = requirements,
      entry_points= {
          "console_scripts": [
              "cognition-datasources=datasources.scripts._cli:cognition_datasources"
          ]},
      include_package_data=True
      )