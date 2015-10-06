from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

base = 'Console'

executables = [
    Executable('tc.py', base=base, targetName = 'Pyper')
]

setup(name='Pyper Timesheet Utility',
      version = '0.2',
      description = 'Pyper Timesheet Tracking Utility',
      options = dict(build_exe = buildOptions),
      executables = executables)
