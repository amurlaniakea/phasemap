"""PHASEMAP - diagramas de fase verificables. Nucleo stdlib, sin dependencias."""
from .models.regular import RegularPhase, BinarySystem
from .models.miscibility import MiscibilityGap
from .core.equilibrium import (Segment, PhaseFraction, equilibrium_at, lever,
                               tangent_residual, scan_diagram, Diagram)
from .core.gibbs import R, phase_rule
from .systems.presets import PRESETS, Preset
from .models import water

__version__ = "0.1.0"
