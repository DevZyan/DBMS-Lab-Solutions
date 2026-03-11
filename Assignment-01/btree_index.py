#!/usr/bin/env python3

import json
import os
import sys


class Node:
    def __init__(self, t, leaf, node_id):
        self.t = t
        self.leaf = leaf
        self.id = node_id
        self.keys = []
        self.children = []
        self.ptrs = {}

    def to_dict(self):
        return {
            "id": self.id,
            "leaf": self.leaf,
            "keys": self.keys,
            "children": self.children,
            "ptrs": self.ptrs,
        }

    @staticmethod
    def from_dict(d, t):
        n = Node(t, d["leaf"], d["id"])
        n.keys = d.get("keys", [])
        n.children = d.get("children", [])
        n.ptrs = d.get("ptrs", {})
        return n


class BTree:
    def __init__(self, index_path, max_branching=4):
        self.index_path = index_path
        self.meta_path = index_path + ".meta"
        self.nodes_path = index_path + ".nodes"

        self.max_branching = max_branching
        self.t = max_branching // 2

        self.root_id = -1
        self.next_id = 0
        self.nodes = {}

        if os.path.exists(self.meta_path) and os.path.exists(self.nodes_path):
            self._load()
        else:
            self._new()

    def _new(self):
        root = Node(self.t, True, 0)
        self.nodes[0] = root
        self.root_id = 0
        self.next_id = 1
        self._save()

    def _load(self):
        with open(self.meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.root_id = int(meta["root_id"])
        self.next_id = int(meta["next_id"])

        with open(self.nodes_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.nodes = {int(k): Node.from_dict(v, self.t) for k, v in raw.items()}

    def _save(self):
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump({"root_id": self.root_id, "next_id": self.next_id}, f)

        raw = {str(i): n.to_dict() for i, n in self.nodes.items()}
        with open(self.nodes_path, "w", encoding="utf-8") as f:
            json.dump(raw, f)

    def _new_id(self):
        nid = self.next_id
        self.next_id += 1
        return nid

    def _make_node(self, leaf):
        nid = self._new_id()
        n = Node(self.t, leaf, nid)
        self.nodes[nid] = n
        return n

    def insert(self, key, ptr):
        root = self.nodes[self.root_id]
        if len(root.keys) >= 2 * self.t - 1:
            new_root = self._make_node(False)
            new_root.children = [self.root_id]
            self.root_id = new_root.id
            self._split_child(new_root, 0)
        self._insert_non_full(self.root_id, key, ptr)

    def _insert_non_full(self, node_id, key, ptr):
        node = self.nodes[node_id]

        if node.leaf:
            i = len(node.keys) - 1
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
            node.ptrs[key] = ptr
            return

        i = len(node.keys) - 1
        while i >= 0 and key < node.keys[i]:
            i -= 1
        i += 1

        child = self.nodes[node.children[i]]
        if len(child.keys) >= 2 * self.t - 1:
            self._split_child(node, i)
            if key > node.keys[i]:
                i += 1

        self._insert_non_full(node.children[i], key, ptr)

    def _split_child(self, parent, child_index):
        child_id = parent.children[child_index]
        child = self.nodes[child_id]

        right = self._make_node(child.leaf)

        mid = self.t - 1
        mid_key = child.keys[mid]
        mid_ptr = child.ptrs.get(mid_key)

        right.keys = child.keys[mid + 1 :]
        child.keys = child.keys[:mid]

        for k in right.keys:
            if k in child.ptrs:
                right.ptrs[k] = child.ptrs[k]
                del child.ptrs[k]
        if mid_key in child.ptrs:
            del child.ptrs[mid_key]

        if not child.leaf:
            right.children = child.children[mid + 1 :]
            child.children = child.children[: mid + 1]

        parent.keys.insert(child_index, mid_key)
        parent.children.insert(child_index + 1, right.id)
        if mid_ptr is not None:
            parent.ptrs[mid_key] = mid_ptr

    def search(self, key):
        return self._search(self.root_id, key)

    def _search(self, node_id, key):
        node = self.nodes[node_id]
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and node.keys[i] == key:
            if key in node.ptrs:
                return node.ptrs[key]
            if node.leaf:
                return None
            return self._search(node.children[i], key)

        if node.leaf:
            return None
        if i >= len(node.children):
            return None
        return self._search(node.children[i], key)


def build_index(csv_path, index_path):
    tree = BTree(index_path)

    with open(csv_path, "rb") as fb:
        header = fb.readline()
        if not header:
            tree._save()
            return

        while True:
            pos = fb.tell()
            line = fb.readline()
            if not line:
                break
            if line.strip():
                first = line.split(b",", 1)[0].decode("utf-8", errors="replace")
                tree.insert(first, pos)

    tree._save()


def fetch_record(csv_path, pos):
    with open(csv_path, "rb") as fb:
        header_bytes = fb.readline()
        fb.seek(pos)

        line = fb.readline()
        if not line:
            return None, None

        header = header_bytes.decode("utf-8", errors="replace").rstrip("\r\n")
        record = line.decode("utf-8", errors="replace").rstrip("\r\n")
        return header, record


def main():
    if len(sys.argv) != 3:
        print("Usage: python btree_index.py <csv_file> <primary_key_value>")
        return 1

    csv_path = sys.argv[1]
    key = sys.argv[2]
    index_path = csv_path + ".btree_index"

    if not os.path.exists(csv_path):
        print(f"Error: File '{csv_path}' not found.")
        return 1

    if not (
        os.path.exists(index_path + ".meta") and os.path.exists(index_path + ".nodes")
    ):
        build_index(csv_path, index_path)

    tree = BTree(index_path)
    pos = tree.search(key)

    if pos is None:
        print(f"Record with primary key '{key}' not found.")
        return 0

    header, record = fetch_record(csv_path, pos)
    if record is None:
        print("Error: Record not found at stored offset")
        return 1

    print(header)
    print(record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
