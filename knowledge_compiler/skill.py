"""
Skill — agent-accessible knowledge base built from compiled objects.

Loads a book's registry and object store, then provides a simple API:

    skill = Skill("books/acsm12")
    obj  = skill.get("threshold.bmi_classification")
    name = skill.resolve("BMI Classification")
"""

import os
import yaml


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class UnknownObjectError(KeyError):
    """Raised when an object ID is not found in the registry."""


class Skill:
    """A typed knowledge base compiled from a textbook."""

    def __init__(self, book_path):
        """
        Args:
            book_path: Path to the book directory, e.g. "books/acsm12".
                       Relative paths are resolved from the project root.
        """
        if not os.path.isabs(book_path):
            book_path = os.path.join(ROOT, book_path)
        self._book_path = book_path

        # Load registry
        reg_path = os.path.join(book_path, "registry.yaml")
        if not os.path.exists(reg_path):
            raise FileNotFoundError(f"Registry not found: {reg_path}")
        with open(reg_path, encoding="utf-8") as f:
            self._registry = yaml.safe_load(f).get("registry", {})

        # Index objects by ID -> (type_dir, file_path)
        self._index = {}
        objects_dir = os.path.join(book_path, "objects")
        if os.path.isdir(objects_dir):
            for type_dir in os.listdir(objects_dir):
                type_path = os.path.join(objects_dir, type_dir)
                if not os.path.isdir(type_path):
                    continue
                for fname in os.listdir(type_path):
                    if not fname.endswith(".yaml"):
                        continue
                    obj_id = fname[:-5]  # strip .yaml
                    self._index[obj_id] = (type_dir, os.path.join(type_path, fname))

    # ── Public API ──────────────────────────────────────────────

    def get(self, identifier):
        """
        Retrieve a compiled knowledge object by its ID.

        Args:
            identifier: Object ID (e.g. "concept.exercise") or
                        canonical name (e.g. "Exercise").

        Returns:
            The parsed YAML object as a dict.

        Raises:
            UnknownObjectError: If the identifier is not found.
        """
        # Try as canonical name first (reverse lookup)
        for name, oid in self._registry.items():
            if name == identifier:
                identifier = oid
                break

        # Try as object ID
        if identifier in self._index:
            type_dir, path = self._index[identifier]
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f)

        # Try direct file path (for type-qualified lookups in registry)
        for name, oid in self._registry.items():
            if oid == identifier:
                if oid in self._index:
                    type_dir, path = self._index[oid]
                    with open(path, encoding="utf-8") as f:
                        return yaml.safe_load(f)

        raise UnknownObjectError(
            f"Unknown object: '{identifier}'. "
            f"Available IDs: {list(self._index.keys())[:20]}..."
        )

    def resolve(self, name):
        """
        Resolve a canonical name to its object ID.

        Args:
            name: Canonical name as it appears in the registry
                  (e.g. "Exercise", "BMI Classification").

        Returns:
            The object ID string, or None if not found.
        """
        return self._registry.get(name)

    def list_objects(self):
        """Return all (object_id, type_dir) pairs in the skill."""
        return list(self._index.items())

    def list_types(self):
        """Return a dict of type -> count of objects."""
        counts = {}
        for type_dir, _ in self._index.values():
            counts[type_dir] = counts.get(type_dir, 0) + 1
        return counts

    @property
    def registry(self):
        """The canonical name -> object ID mapping."""
        return dict(self._registry)
