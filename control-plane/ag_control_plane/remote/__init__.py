"""
Jarvis Remote Control Plane Package
Provides secure, authenticated pairing and remote control between iPhone and Mac.
Strictly conforms to JARVIS_ARCHITECTURE_LOCK.
"""

from .pairing import PairingManager, PairedDevice
from .server import JarvisRemoteServer

__all__ = ["PairingManager", "PairedDevice", "JarvisRemoteServer"]
