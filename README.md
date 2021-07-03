# VisTree

A simple tool to visualize taxonomy trees.



## Prerequisites

> python==3.7.4, pyyaml==5.1.2, networkx==2.5.1, matplotlib==3.1.1, pygraphviz==1.3



## Basic Usage

Specify the path to the input `yaml` file and run

```shell
python vis_tree.py PATH/TO/YOUR/INPUT/YAML/FILE
```

The `yaml` file should contain the *hierarchy*, which is something like:

```yaml
A:
  AA1:
  AA2:
B:
  BB1:
  BB2:
    BBB1:
    BBB2:
    BBB3:
    BBB4:
    BBB5:
    BBB6:
C:
  CC1:
    CCC1:
  CC2:
```

**Note that for the leaf nodes an ending colon is also required.**