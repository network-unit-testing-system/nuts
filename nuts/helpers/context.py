"""
Context helper functions
"""
import types
from nuts.context import NutsContext
from typing import Dict, List, Any


def load_context(module: types.ModuleType, params: List[Dict[str, Any]]) -> NutsContext:
    context_class = getattr(module, "CONTEXT", NutsContext)
    ctx = context_class(params)
    ctx.initialize()
    return ctx
