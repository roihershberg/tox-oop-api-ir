from distutils.core import setup

setup(name='ref_link_fixer',
      version='0.1',
      py_modules=['reference_link_fixer'],
      entry_points={
          'mkdocs.plugins': [
              'reflinkfixer = reference_link_fixer:ReferenceLinkFixer',
          ]
      },
      install_requires=[
          'beautifulsoup4'
      ],
      )
