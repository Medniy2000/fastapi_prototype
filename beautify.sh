

pip install --upgrade pip

# Beautify project's code
echo "💥 Black formatter is checking.. ⏳ "
poetry run black .
echo "Black formatter finished! 💎"

echo "💥 Flake8 in checking.. ⏳ "
flake8 .
echo "Flake8 finished! 💎"

echo "💥 MyPy is checking.. ⏳ "
rm -rf .mypy_cache  # clear cache
poetry run mypy --install-types --non-interactive  --config-file ./pyproject.toml src/
echo "MyPy finished! 💎"
