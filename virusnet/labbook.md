# Labbook

## 2023-08-02

Installed in base env boa

```
 micromamba install boa -c conda-forge
 micromamba activate /Users/user/miniconda3
 conda mambabuild conda.recipe
```

It worked till

```
## Package Plan ##
 environment location: /Users/user/miniconda3/conda-bld/virusnet_1690970553875/_build_env
 +DEBUG_CXXFLAGS=-march=core2 -mtune=haswell -mssse3 -ftree-vectorize -fPIC -fPIE -fstack-protector-strong -O2 -pipe -stdlib=libc++ -fvisibility-inlines-hidden -std=c++14 -fmessage-length=0 -Og -g -Wall -Wextra -isystem $PREFIX/include -fdebug-prefix-map=$SRC_DIR=/usr/local/src/conda/virusnet-0.1.0 -fdebug-prefix-map=$PREFIX=/usr/local/src/conda-prefix
Warnung: ung"ultiges Paket '.'
Fehler: Fehler: keine Pakete angegeben
Traceback (most recent call last):
  File "/Users/user/miniconda3/bin/conda-mambabuild", line 10, in <module>
    sys.exit(main())
  File "/Users/user/miniconda3/lib/python3.10/site-packages/boa/cli/mambabuild.py", line 256, in main
    call_conda_build(action, config)
  File "/Users/user/miniconda3/lib/python3.10/site-packages/boa/cli/mambabuild.py", line 228, in call_conda_build
    result = api.build(
  File "/Users/user/miniconda3/lib/python3.10/site-packages/conda_build/api.py", line 180, in build
    return build_tree(
  File "/Users/user/miniconda3/lib/python3.10/site-packages/conda_build/build.py", line 3078, in build_tree
    packages_from_this = build(metadata, stats,
  File "/Users/user/miniconda3/lib/python3.10/site-packages/conda_build/build.py", line 2198, in build
    utils.check_call_env(cmd, env=env, rewrite_stdout_env=rewrite_env,
  File "/Users/user/miniconda3/lib/python3.10/site-packages/conda_build/utils.py", line 451, in check_call_env
    return _func_defaulting_env_to_os_environ("call", *popenargs, **kwargs)
  File "/Users/user/miniconda3/lib/python3.10/site-packages/conda_build/utils.py", line 427, in _func_defaulting_env_to_os_environ
    raise subprocess.CalledProcessError(proc.returncode, _args)
subprocess.CalledProcessError: Command '['/bin/bash', '-o', 'errexit', '/Users/user/miniconda3/conda-bld/virusnet_1690970553875/work/conda_build.sh']' returned non-zero exit status 1.
```

\-> it seems that the error is the `conda_build.sh` script, so the error is on my side. However, I only have a `build.sh` file, but the content of the file is similar to mine

```
if [ -z ${CONDA_BUILD+x} ]; then
   source /Users/user/miniconda3/conda-bld/virusnet_1690970553875/work/build_env_setup.sh
fi
#!/bin/bash
$R CMD INSTALL --build .
# Download the model
wget -P $PREFIX/lib/virusnet https://f000.backblazeb2.com/file/genomenet/models/virus_genus_2023-01-23.hdf5
```

Added now

```
script_env:
- VIRUSNET_GENUS_MODEL_PATH
```

and changed test command

```
test:
commands:
- bash ${RECIPE_DIR}/build.sh
```

Restart build now with

```
 conda mambabuild conda.recipe 2>&1 | tee build2023-08-02-12:30.log
```

Based on output I can specify versions

- h5py:                     3.3.0-nompi_py37hdf859c4_100
- r-base:                   3.5.1-hc03ab29_1012
- tensorflow:               1.14.0-h3cdfc77_0

Get the error

```
Packaging virusnet
INFO:conda_build.build:Packaging virusnet
/Users/user/miniconda3/lib/python3.10/site-packages/conda_build/environ.py:494: UserWarning: The environment variable 'VIRUSNET_GENUS_MODEL_PATH' is undefined.
  warnings.warn(
Packaging virusnet-0.1.0-pyr35_0
INFO:conda_build.build:Packaging virusnet-0.1.0-pyr35_0
DEBUG:conda_build.noarch_python:Don't know how to handle file: lib/virusnet/virus_genus_2023-01-23.hdf5.  Including it as-is.
number of files: 2
Fixing permissions
Traceback (most recent call last):
  File "/Users/user/miniconda3/bin/conda-mambabuild", line 10, in <module>
    sys.exit(main())
  File "/Users/user/miniconda3/lib/python3.10/site-packages/boa/cli/mambabuild.py", line 256, in main
    call_conda_build(action, config)
  File "/Users/user/miniconda3/lib/python3.10/site-packages/boa/cli/mambabuild.py", line 228, in call_conda_build
    result = api.build(
  File "/Users/user/miniconda3/lib/python3.10/site-packages/conda_build/api.py", line 180, in build
    return build_tree(
  File "/Users/user/miniconda3/lib/python3.10/site-packages/conda_build/build.py", line 3078, in build_tree
    packages_from_this = build(metadata, stats,
  File "/Users/user/miniconda3/lib/python3.10/site-packages/conda_build/build.py", line 2358, in build
    newly_built_packages = bundlers[pkg_type](output_d, m, env, stats)
  File "/Users/user/miniconda3/lib/python3.10/site-packages/conda_build/build.py", line 1672, in bundle_conda
    output['checksums'] = create_info_files(metadata, replacements, files, prefix=metadata.config.host_prefix)
  File "/Users/user/miniconda3/lib/python3.10/site-packages/conda_build/build.py", line 1272, in create_info_files
    copy_license(m)
  File "/Users/user/miniconda3/lib/python3.10/site-packages/conda_build/build.py", line 762, in copy_license
    generic_copy(m, "license", "license_file")
  File "/Users/user/miniconda3/lib/python3.10/site-packages/conda_build/build.py", line 800, in generic_copy
    raise ValueError(
ValueError: License file given in about/license_file (/Users/user/VirusNet/conda.recipe/LICENSE) does not exist in source root dir or in recipe root dir (with meta.yaml)
```

Need to try out if var is set.

Made the changes to the scripts/ folder (link/unlink) and changed path to LICENCE and re-run. I also now changed that r-base should be >= 4.0 which I expect to cause problems.

```
 conda mambabuild conda.recipe 2>&1 | tee build2023-08-02-12:49.log
```

Now version:

- python:                    3.11.4-h30d4d87_0_cpython     conda-forge
- r-base:                    4.3.1-had2b78c_3              conda-forge
- r-devtools:                2.4.5-r43hc72bb7e_2           conda-forge
- r-zoo:                     1.8_12-r43h6dc245f_1          conda-forge
- tensorflow:                2.12.1-cpu_py311hfac9faf_0    conda-forge
- hdf5:                      1.14.1-nompi_hedada53_100     conda-forge
- h5py:                      3.9.0-nompi_py311hc915cd5_101 conda-forge
- keras:                     2.12.0-pyhd8ed1ab_0           conda-forge
- r-optparse:                1.7.3-r43hc72bb7e_2           conda-forge

```
conda mambabuild conda.recipe --output-folder build 2>&1 | tee build2023-08-02-14:50.log
```

Need to check if variable `echo $VIRUSNET_GENUS_MODEL_PATH` is set properly.

```
micromamba create -n test_env
micromamba activate test_env
micromamba install -c file://$(pwd)/build virusnet
```

ChatGPT mentioned I should copy stuff to bin folder (in build.sh), added this

```
conda mambabuild conda.recipe --output-folder build 2>&1 | tee build2023-08-02-15:55.log
```

Hm, ChatGPT dows not know whats causing the error I have. It is not founding the virusnet.py and throwing an error. I added `**echo** "SRC_DIR is set to $SRC_DIR"` to the `build.sh` file and will see now hopefully what the problem is.
