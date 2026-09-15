"""Dataset adapters for PAMIR-CUAS validation."""

from .mmaud import build_incident as build_mmaud_incident

__all__ = ["build_mmaud_incident"]
