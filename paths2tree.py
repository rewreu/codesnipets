## generate from bing chat
from collections import defaultdict

def build_tree(paths):
    tree = defaultdict(dict)
    for path in paths:
        parts = path.split('/')
        current = tree
        for part in parts:
            current = current.setdefault(part, {})
    return tree

def display_tree(tree, level=0):
    for key in sorted(tree.keys()):
        print('  ' * level + key)
        display_tree(tree[key], level+1)

paths = ['/home/user/target/var/file2.txt','/home/user/file1.txt', '/home/user/file2.txt', '/home/user/dir/file3.txt']
tree = build_tree(paths)
display_tree(tree)
