from setuptools import setup, find_packages

with open('./requirements.txt') as reqs:
    requirements = [line.rstrip() for line in reqs]

setup(name="cognition_datasources",
      version='0.1',
      author='Jeff Albrecht',
      author_email='geospatialjeff@gmail.com',
      packages=find_packages(exclude=['tests', 'static/cbers/cbers_reference.geojson', 'static/naip/coverages', 'utils', 'docs']),
      install_requires = requirements,
      entry_points= {
          "console_scripts": [
              "cognition-datasources=scripts._cli:cognition_datasources"
          ]
      }
      )