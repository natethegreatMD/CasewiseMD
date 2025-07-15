"""
MCP Server for CasewiseMD
Handles Model Context Protocol communication and tool orchestration
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

from ..tools.viewer_tools import ViewerTools
from ..tools.case_tools import CaseTools

logger = logging.getLogger(__name__)

class MCPRequest(BaseModel):
    """MCP request model"""
    tool: str
    parameters: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    """MCP response model"""
    success: bool
    data: Dict[str, Any] = {}
    error: Optional[str] = None

class MCPServer:
    """MCP Server for CasewiseMD platform"""
    
    def __init__(self):
        self.viewer_tools = ViewerTools()
        self.case_tools = CaseTools()
        
        # Register available tools
        self.available_tools = {
            # Viewer tools
            "get_case_viewer_url": self.viewer_tools.get_case_viewer_url,
            "get_case_metadata": self.viewer_tools.get_case_metadata,
            "list_available_cases": self.viewer_tools.list_available_cases,
            
            # Case management tools
            "get_case_info": self.case_tools.get_case_info,
            "search_cases": self.case_tools.search_cases,
            "get_case_statistics": self.case_tools.get_case_statistics,
        }
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        Handle MCP tool request
        
        Args:
            request: MCP request with tool name and parameters
            
        Returns:
            MCP response with tool results
        """
        try:
            tool_name = request.tool
            parameters = request.parameters
            
            # Check if tool exists
            if tool_name not in self.available_tools:
                return MCPResponse(
                    success=False,
                    error=f"Tool '{tool_name}' not found. Available tools: {list(self.available_tools.keys())}"
                )
            
            # Get tool function
            tool_function = self.available_tools[tool_name]
            
            # Call tool with parameters
            result = await tool_function(**parameters)
            
            return MCPResponse(
                success=True,
                data=result
            )
            
        except TypeError as e:
            # Handle parameter errors
            return MCPResponse(
                success=False,
                error=f"Invalid parameters for tool '{request.tool}': {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error handling MCP request: {str(e)}")
            return MCPResponse(
                success=False,
                error=f"Internal server error: {str(e)}"
            )
    
    def get_tool_schema(self) -> Dict[str, Any]:
        """
        Get schema for all available tools
        
        Returns:
            Dictionary with tool schemas
        """
        return {
            "tools": [
                {
                    "name": "get_case_viewer_url",
                    "description": "Get OHIF viewer URL for a specific case",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "case_id": {
                                "type": "string",
                                "description": "Case identifier (e.g., 'case001')"
                            }
                        },
                        "required": ["case_id"]
                    }
                },
                {
                    "name": "get_case_metadata",
                    "description": "Get metadata for a specific case",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "case_id": {
                                "type": "string",
                                "description": "Case identifier"
                            }
                        },
                        "required": ["case_id"]
                    }
                },
                {
                    "name": "list_available_cases",
                    "description": "List all available cases",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "get_case_info",
                    "description": "Get comprehensive case information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "case_id": {
                                "type": "string",
                                "description": "Case identifier"
                            }
                        },
                        "required": ["case_id"]
                    }
                },
                {
                    "name": "search_cases",
                    "description": "Search and filter cases",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Text search query"
                            },
                            "modality": {
                                "type": "string",
                                "description": "Filter by modality (CT, MR, etc.)"
                            },
                            "body_region": {
                                "type": "string",
                                "description": "Filter by body region"
                            },
                            "difficulty": {
                                "type": "string",
                                "description": "Filter by difficulty level"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by tags"
                            }
                        }
                    }
                },
                {
                    "name": "get_case_statistics",
                    "description": "Get case statistics and summary",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    
    async def test_tools(self) -> Dict[str, Any]:
        """
        Test all available tools
        
        Returns:
            Dictionary with test results
        """
        test_results = {}
        
        try:
            # Test viewer tools
            test_results["get_case_viewer_url"] = await self.viewer_tools.get_case_viewer_url("case001")
            test_results["get_case_metadata"] = await self.viewer_tools.get_case_metadata("case001")
            test_results["list_available_cases"] = await self.viewer_tools.list_available_cases()
            
            # Test case tools
            test_results["get_case_info"] = await self.case_tools.get_case_info("case001")
            test_results["search_cases"] = await self.case_tools.search_cases(modality="CT")
            test_results["get_case_statistics"] = await self.case_tools.get_case_statistics()
            
            return {
                "success": True,
                "test_results": test_results
            }
            
        except Exception as e:
            logger.error(f"Error testing tools: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Create FastAPI app for MCP server
app = FastAPI(title="CasewiseMD MCP Server", version="1.0.0")
mcp_server = MCPServer()

@app.post("/mcp/request")
async def handle_mcp_request(request: MCPRequest) -> MCPResponse:
    """Handle MCP tool requests"""
    return await mcp_server.handle_request(request)

@app.get("/mcp/schema")
async def get_tool_schema():
    """Get tool schema"""
    return mcp_server.get_tool_schema()

@app.get("/mcp/test")
async def test_tools():
    """Test all available tools"""
    return await mcp_server.test_tools()

@app.get("/mcp/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "server": "CasewiseMD MCP Server"} 