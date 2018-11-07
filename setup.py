from setuptools import setup


setup(name='StatisticsStackOverflow',
      version='1',
      author='Marios Tsigkas',
      author_email='mariosh346@gmail.com',
      long_description=open('README.md').read(),
      scripts=['stats.py', 'test/test_stats.py'],
      install_requires=[
          'mock',
          'stackapi'
      ],
      include_package_data=True,
      )