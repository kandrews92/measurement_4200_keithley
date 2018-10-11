from distutils.core import setup
setup(
  name = 'measurement_4200_keithley',         # How you named your package folder (MyLib)
  packages = ['measurement_4200_keithley'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Excel analysis of FETs with 4200 Keithley semiconductor analyzer',   # Give a short description about your library
  author = 'Kraig Andrews',                   # Type in your name
  author_email = 'kraigandrews1992@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/kandrews92/measurement_4200_keithley',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['Semiconductor', 'Excel', 'Keithley'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'numpy',
          'matplotlib',
          'xlrd',
          'openpyxl',
          'xlwt',
          'scipy',
      ],
      classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package

    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',

    'License :: OSI Approved :: MIT License',   # Again, pick a license

    'Programming Language :: Python :: 2',      #Specify which python versions that you want to support
    'Programming Language :: Python :: 2.7',
  ],
)