# lightspeed-providers
Source code for our custom providers.

## Building and publishing

Manual procedure, assuming an existing PyPI API token available:

    ## Generate distribution archives to be uploaded into Python registry
    pdm run python -m build
    ## Upload distribution archives into Python registry
    pdm run python -m twine upload --repository ${PYTHON_REGISTRY} dist/*
