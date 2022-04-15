# PlasticineLab: A Soft-Body Manipulation Benchmark with Differentiable Physics

## Usage
 - Install `python3 -m pip install -e .`
 - Run `python3 -m plb.algorithms.solve --algo [algo] --env_name [env_name] --path [output-dir]`. It will run algorithms `algo` for environment `env-name` and store results in `output-dir`. For example
    `python3 -m plb.algorithms.solve --algo action --env_name Move-v1 --path output` will run call an Adam optimizer to optimize an action sequence in environment `Move-v1`

# eric stuff

install stuff in venv; messy, but just spam until it works?

```sh
python3 -m venv ./venv
source ./venv/bin/activate
pip install -U pip wheel
pip install tensorflow==2.8.0
pip install torch==1.7.1+cu110 -f https://download.pytorch.org/whl/torch_stable.html
pip install -r ./extra_reqs.txt
pip install -e .
pip freeze > ./requirements.freeze.txt
```

run dough thing

```sh
source ./venv/bin/activate
python -m plb.envs.sim_with_joystick
```
