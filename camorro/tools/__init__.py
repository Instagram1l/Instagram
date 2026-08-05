"""تجميع المنفذ الكامل من كل فئات الأدوات"""
from .executor import BaseExecutor
from .recon import ReconTools
from .scanning import ScanningTools
from .exploitation import ExploitationTools
from .vulnsearch import VulnSearchTools


class ToolExecutor(BaseExecutor, ReconTools, ScanningTools, ExploitationTools, VulnSearchTools):
    """المنفذ الكامل — يجمع كل الأدوات الـ14 في كائن واحد"""
    pass


__all__ = ["ToolExecutor"]
