"""Device utility to manage CPU / CUDA acceleration safely."""

import torch

def get_device(prefer_cuda: bool = True) -> torch.device:
    """Detect and return the appropriate torch device with fallback to CPU.
    
    Args:
        prefer_cuda: If True and CUDA is available, returns 'cuda', otherwise 'cpu'.
        
    Returns:
        torch.device
    """
    if prefer_cuda and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def get_device_info() -> dict:
    """Return runtime hardware device diagnostic info."""
    cuda_available = torch.cuda.is_available()
    info = {
        "cuda_available": cuda_available,
        "device_name": torch.cuda.get_device_name(0) if cuda_available else "CPU",
        "device_count": torch.cuda.device_count() if cuda_available else 0,
        "torch_version": torch.__version__
    }
    return info
