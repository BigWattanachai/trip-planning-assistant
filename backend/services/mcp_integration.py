import os
import aiohttp
from typing import Dict, Any, Optional
from google.adk.tools import mcp_tool
from google.adk.tools.mcp import MCPConfig
from dotenv import load_dotenv

load_dotenv()

class MCPIntegration:
    def __init__(self):
        self.server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:8080")
        self.api_key = os.getenv("MCP_API_KEY")
        
        # Configure MCP
        self.mcp_config = MCPConfig(
            server_url=self.server_url,
            api_key=self.api_key,
            retry_attempts=3,
            retry_delay=1,
            ssl_verify=True,
            custom_headers={"X-Client": "travel-a2a"}
        )
        
        # Create MCP tool
        self.mcp_tool = mcp_tool(config=self.mcp_config)
    
    async def search_flights_via_mcp(self, params: Dict) -> Dict:
        """Search flights using MCP integration"""
        try:
            response = await self.mcp_tool.execute({
                "operation": "search_flights",
                "params": params
            })
            return response
        except Exception as e:
            print(f"MCP flight search error: {e}")
            return {"error": str(e)}
    
    async def search_hotels_via_mcp(self, params: Dict) -> Dict:
        """Search hotels using MCP integration"""
        try:
            response = await self.mcp_tool.execute({
                "operation": "search_hotels",
                "params": params
            })
            return response
        except Exception as e:
            print(f"MCP hotel search error: {e}")
            return {"error": str(e)}
    
    async def search_activities_via_mcp(self, params: Dict) -> Dict:
        """Search activities using MCP integration"""
        try:
            response = await self.mcp_tool.execute({
                "operation": "search_activities",
                "params": params
            })
            return response
        except Exception as e:
            print(f"MCP activity search error: {e}")
            return {"error": str(e)}
    
    async def get_destination_info_via_mcp(self, destination: str) -> Dict:
        """Get destination information using MCP integration"""
        try:
            response = await self.mcp_tool.execute({
                "operation": "get_destination_info",
                "params": {"destination": destination}
            })
            return response
        except Exception as e:
            print(f"MCP destination info error: {e}")
            return {"error": str(e)}
    
    async def search_restaurants_via_mcp(self, params: Dict) -> Dict:
        """Search restaurants using MCP integration"""
        try:
            response = await self.mcp_tool.execute({
                "operation": "search_restaurants",
                "params": params
            })
            return response
        except Exception as e:
            print(f"MCP restaurant search error: {e}")
            return {"error": str(e)}
    
    async def get_weather_forecast(self, destination: str, dates: Dict) -> Dict:
        """Get weather forecast for destination using MCP"""
        try:
            response = await self.mcp_tool.execute({
                "operation": "get_weather_forecast",
                "params": {
                    "location": destination,
                    "start_date": dates.get("start_date"),
                    "end_date": dates.get("end_date")
                }
            })
            return response
        except Exception as e:
            print(f"MCP weather forecast error: {e}")
            return {"error": str(e)}
    
    async def get_exchange_rates(self, base_currency: str, target_currencies: list) -> Dict:
        """Get currency exchange rates using MCP"""
        try:
            response = await self.mcp_tool.execute({
                "operation": "get_exchange_rates",
                "params": {
                    "base": base_currency,
                    "targets": target_currencies
                }
            })
            return response
        except Exception as e:
            print(f"MCP exchange rates error: {e}")
            return {"error": str(e)}
