from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PipelineData(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

@app.post("/pipelines/parse")
async def parse_pipeline(data: PipelineData):
    try:
        nodes = data.nodes
        edges = data.edges
        
        def is_dag(nodes, edges):
            # Build adjacency list
            if not nodes:
                return True
                
            graph = {node['id']: [] for node in nodes}
            
            # Add edges to graph
            for edge in edges:
                source = edge.get('source')
                target = edge.get('target')
                if source and target:
                    if source in graph:
                        graph[source].append(target)
            
            # Cycle detection using DFS
            visited = set()
            rec_stack = set()
            
            def has_cycle(node):
                if node in rec_stack:
                    return True  # Back edge found - cycle detected
                if node in visited:
                    return False
                
                visited.add(node)
                rec_stack.add(node)
                
                # Visit all neighbors
                for neighbor in graph.get(node, []):
                    if has_cycle(neighbor):
                        return True
                
                rec_stack.remove(node)
                return False
            
            # Check all nodes for cycles
            for node_id in graph:
                if node_id not in visited:
                    if has_cycle(node_id):
                        return False
            
            return True
        
        result = {
            "num_nodes": len(nodes),
            "num_edges": len(edges),
            "is_dag": is_dag(nodes, edges)
        }
        
        print(f"Pipeline analysis: {result}")
        return result
        
    except Exception as e:
        print(f"Error processing pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "VectorShift Backend API"}
