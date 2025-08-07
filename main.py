from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

# Enable CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend domain
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
            if not nodes:
                return True
                
            graph = {node['id']: [] for node in nodes}
            
            for edge in edges:
                source = edge.get('source')
                target = edge.get('target')
                if source and target and source in graph:
                    graph[source].append(target)
            
            visited = set()
            rec_stack = set()
            
            def has_cycle(node):
                if node in rec_stack:
                    return True
                if node in visited:
                    return False
                
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in graph.get(node, []):
                    if has_cycle(neighbor):
                        return True
                
                rec_stack.remove(node)
                return False
            
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
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "VectorShift Backend API - Running on Back4App"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
