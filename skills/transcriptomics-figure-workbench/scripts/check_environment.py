"""Read-only import/version check. No installation or auto-upgrade."""
import importlib
import platform
print('Python',platform.python_version())
for name in ['matplotlib','pandas','numpy','seaborn','scanpy','anndata','scvelo','squidpy','networkx','sklearn','plotly','upsetplot','shap']:
    try:
        mod=importlib.import_module(name)
        print(name,getattr(mod,'__version__','IMPORTED_VERSION_UNKNOWN'),sep='\t')
    except Exception as exc:
        print(name,'UNAVAILABLE_OR_IMPORT_FAILED',type(exc).__name__,sep='\t')
