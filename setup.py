from setuptools import setup

install_requires = [
      'scipy', 'numpy', 'torch', 'opencv-python', 'tqdm', 'taichi', 'gym', 'tensorboard', 'yacs',
      # HACK: See https://github.com/hzaskywalker/PlasticineLab/issues/3
      'git+https://github.com/openai/baselines@ea25b9e8',
]

setup(name='plb',
      version='0.0.1',
      install_requires=install_requires,
      )
