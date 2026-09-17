"""
Dataset Package — Person 2.
UPI Transaction Fraud Forensics Platform.
"""

from . import config
from .templates import generate_originals, generate_fictional_record, RENDERERS
from .manipulate import generate_manipulated_dataset, MANIPULATORS
from .split import split_dataset
from .audit import audit_dataset_integrity

__all__ = [
    "config",
    "generate_originals",
    "generate_fictional_record",
    "RENDERERS",
    "generate_manipulated_dataset",
    "MANIPULATORS",
    "split_dataset",
    "audit_dataset_integrity",
]
