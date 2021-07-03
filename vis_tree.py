import sys
import math
import operator
from collections.abc import MutableMapping
from itertools import cycle

import yaml
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout


ROOT_TAG = 'Root'

FIG_PATH = './vis_tree.png'

NODE_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
EDGE_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# TODO: 自适应文字大小
TEXT_SIZE = 15
ROTATE_TEXT_ON = True
EXTRA_ROTATION_ANGLE = 90

MARGIN_X = 10
MARGIN_Y = 10
FIG_SIZE = (10, 10)


def parse_file(path):
    with open(path, 'r') as f:
        hierarchy = yaml.load(f, Loader=yaml.FullLoader)
    return hierarchy


def build_tree(hierarchy):
    # 暴力法之嵌套字典转树
    def _build_tree(hierarchy, tree, parent):
        if hierarchy is None:
            return
        for tag, subhierarchy in hierarchy.items():
            tree.add_node(tag)
            tree.add_edge(parent, tag)
            # 管它什么优先，只要hash了每个节点、边都连对了就行
            _build_tree(subhierarchy, tree, tag)
        return tree
    tree = nx.DiGraph()
    # 创建根节点
    tree.add_node(ROOT_TAG)
    return _build_tree(hierarchy, tree, ROOT_TAG)


def draw_tree(tree, save=True):
    _COLOR_ATTR = 'ColOR'
    # 就不考虑效率了害
    # 我就想这样写，快乐就够了
    class _Const:
        _all_instances = dict()
        def __init__(self):
            self.locked = False
        def __set_name__(self, owner, name):
            self.name = '_'+name
        def __set__(self, obj, val):
            if not self.locked:
                setattr(obj, self.name, val)
                self.locked = True
            else:
                raise RuntimeError
        def __get__(self, obj, objtype=None):
            return getattr(obj, self.name)

    class _NormedPos(MutableMapping):
        margin_x = _Const()
        margin_y = _Const()
        def __init__(self, pos, margin_x=0, margin_y=0):
            self.ori = pos
            self.margin_x = margin_x
            self.margin_y = margin_y
            self.max_x = max(map(operator.itemgetter(0), pos.values()))+margin_x
            self.min_x = min(map(operator.itemgetter(0), pos.values()))-margin_x
            self.max_y = max(map(operator.itemgetter(1), pos.values()))+margin_y
            self.min_y = min(map(operator.itemgetter(1), pos.values()))-margin_y
        def __getitem__(self, key):
            x,y = self.ori[key]
            return (x-self.min_x)/(self.max_x-self.min_x), (y-self.min_y)/(self.max_y-self.min_y)
        def __setitem__(self, key, val):
            self.ori[key] = val
            self._update_border_info(*val)
        def __delitem__(self, key):
            # 删除是不允许的
            raise RuntimeError
        def __iter__(self):
            return iter(self.ori)
        def __len__(self):
            return len(self.ori)
        def _update_border_info(self, x, y):
            if x + margin_x > self.max_x:
                self.max_x = x+margin_x
            elif x - margin_x < self.min_x:
                self.min_x = x-margin_x
            if y + margin_y > self.max_y:
                self.max_y = y+margin_y
            elif y - margin_y < self.min_y:
                self.min_y = y-margin_y
        def items(self):
            return list(zip(self.keys(), self.values()))
        def keys(self):
            return self.ori.keys()
        def values(self):
            return [self[key] for key in self.keys()]

    def _determine_colors(tree):
        # 对每个以树的第二层节点为根节点的子树赋予不同的颜色
        node_color_cycle = cycle(NODE_COLORS)
        edge_color_cycle = cycle(EDGE_COLORS)
        for node in tree.adj[ROOT_TAG]:
            node_clr = next(node_color_cycle)
            edge_clr = next(edge_color_cycle)
            nodes = [node]
            while len(nodes) > 0:
                node = nodes.pop()
                tree.nodes[node][_COLOR_ATTR] = node_clr
                for from_, to_ in tree.edges(node):
                    tree.edges[from_, to_][_COLOR_ATTR] = edge_clr
                des = tree.successors(node)
                nodes.extend(des)

    def _draw_nodes(tree, pos):
        for tag, (x, y) in pos.items():
            params = dict(
                fontsize=TEXT_SIZE, 
                color=tree.nodes[tag].get(_COLOR_ATTR, 'k'),
                backgroundcolor='w',
                ha='center',
                va='center'
            )
            if ROTATE_TEXT_ON:
                parents = list(tree.predecessors(tag))
                # 树！树！树！
                assert len(parents) in (0,1)
                if len(parents) == 1:
                    # 如果有父节点，以与父节点连过来的射线为旋转基准
                    px, py = pos[parents[0]]
                    angle = math.atan2(py-y, px-x)
                    # 在此基础上大家一起往一个方向转
                    angle = math.degrees(angle)+EXTRA_ROTATION_ANGLE
                    params.update(dict(rotation=angle))
            plt.text(x, y, tag, **params)

    def _draw_edges(tree, pos):
        for from_, to_ in tree.edges:
            clr = tree.edges[from_, to_].get(_COLOR_ATTR, 'k')
            # TODO: 设置线宽
            plt.plot([pos[from_][0], pos[to_][0]], [pos[from_][1], pos[to_][1]], color=clr)

    # 最核心的算法调库实现了，剩下的都是暴力和业务逻辑
    pos = graphviz_layout(tree, prog='twopi', args='')
    normed_pos = _NormedPos(pos, MARGIN_X, MARGIN_Y)
    plt.figure(figsize=FIG_SIZE)
    _determine_colors(tree)
    _draw_nodes(tree, normed_pos)
    _draw_edges(tree, normed_pos)
    # # 暴力法之背景调成白色以及把marker size设大
    # nx.draw_networkx(tree, pos, node_size=3000, alpha=1.0, node_color='white', node_shape='o', with_labels=True)
    # plt.axis('equal')
    plt.axis('off')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    # plt.show()
    if save:
        plt.savefig(FIG_PATH)


if __name__ == '__main__':
    hierarchy = parse_file(sys.argv[1])
    tree = build_tree(hierarchy)
    draw_tree(tree, save=True)