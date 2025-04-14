<p align="center">
    <img src="https://raw.githubusercontent.com/securisec/chepy_plugins/master/logo.png" width="65%">
</p>

[![](https://img.shields.io/readthedocs/chepy-plugins.svg?logo=read-the-docs&label=Docs)](http://chepy-plugins.readthedocs.io/en/latest/)

# Chepy plugins
This repository hosts various Plugins for Chepy. Chepy is extendable with custom plugins. The docs for how to create plugins is [here](https://chepy.readthedocs.io/en/latest/plugins.html). All Chepy plugins extend the `ChepyCore` class. Refere to the docs for available methods and attributes for `ChepyCore`. 

To use this plugins repository, do:

```bash
git clone https://github.com/securisec/chepy_plugins.git
```

Then edit the chepy config file, and set the **pluginpath** to the `chepy_plugin` directory. The config file is located in the `$User/.chepy/chepy.conf`. Example config:

```
[Plugins]
enableplugins = true
pluginpath = /home/test/chepy_plugins

[Cli]
history_path = /home/test/.chepy/chepy_history
prompt_char = >
prompt_colors = #00ffff #ff0000 #ffd700
show_rprompt = false
prompt_rprompt = #00ff48
prompt_bottom_toolbar = #000000
prompt_toolbar_version = #00ff48
prompt_toolbar_states = #60cdd5
prompt_toolbar_buffers = #ff00ff
prompt_toolbar_type = #ffd700
prompt_toolbar_errors = #ff0000
```



```eval_rst
.. toctree::
   :maxdepth: 3
   :caption: Contents:

   plugins/elffile.rst
   plugins/exif.rst
   plugins/extract.rst
   plugins/forensics.rst
   plugins/git.rst
   plugins/ml.rst
   plugins/report.rst
   plugins/pcap.rst
   plugins/pefile.rst
   plugins/protobuf.rst
   plugins/sqlite.rst
   plugins/useragent.rst
   core.rst
   pullreq.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```
