"""
Context helper functions
"""

import types
from typing import Dict, List, Any
from pytest import Config
from nuts.context import NutsContext


def load_context(
    module: types.ModuleType, params: List[Dict[str, Any]], config: Config
) -> NutsContext:
    context_class = getattr(module, "CONTEXT", NutsContext)
    ctx = context_class(params, pytestconfig=config)
    ctx.initialize()
    return ctx
