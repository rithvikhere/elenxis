"""
Dataset Package — Person 2.
UPI Transaction Fraud Forensics Platform.
"""

from . import config
from .templates import generate_originals, generate_fictional_record, RENDERERS

__all__ = ["config", "generate_originals", "generate_fictional_record", "RENDERERS"]
