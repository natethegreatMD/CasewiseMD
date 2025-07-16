"""
MCP (Model Context Protocol) Package for CasewiseMD
Provides tools and server for medical case management and viewer integration
"""

from .server.mcp_server import MCPServer, app as mcp_app
from .tools.viewer_tools import ViewerTools
from .tools.case_tools import CaseTools

__version__ = "1.0.0"

__all__ = ["MCPServer", "ViewerTools", "CaseTools", "mcp_app"] 