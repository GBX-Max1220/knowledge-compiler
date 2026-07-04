# Contributing to Knowledge Compiler

Thanks for your interest! This project is in early stages (v0.1) and contributions of all kinds are welcome.

## How to contribute

### 🐛 Report bugs

Open a [GitHub Issue](https://github.com/GBX-Max1220/knowledge-compiler/issues/new) with:
- What you expected to happen
- What actually happened
- Steps to reproduce (if applicable)

### 💡 Suggest improvements

Open an issue with the label `enhancement`. Some areas we actively want help with:
- New schema types
- Cross-domain generalization (try compiling a textbook from another field)
- Export targets (Neo4j, vector embeddings, JSON-LD)

### 🔧 Submit code

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run validation: `python scripts/validate.py --book acsm12`
5. Submit a pull request

## Development setup

```bash
git clone https://github.com/GBX-Max1220/knowledge-compiler.git
cd knowledge-compiler
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install pyyaml PyPDF2
```

## Code style

- Python: PEP 8
- YAML: 2-space indentation
- Object IDs: `snake_case`, no source prefix

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
