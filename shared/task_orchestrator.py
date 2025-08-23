"""
Task Orchestrator for MESH A2A Integration
Manages multi-agent workflows and task coordination
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from shared.agent_manager import agent_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class WorkflowStep:
    """A single step in a workflow"""
    step_id: str
    name: str
    task_type: str
    target_agent: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class Workflow:
    """A complete workflow definition"""
    workflow_id: str
    name: str
    steps: List[WorkflowStep]
    status: WorkflowStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    input_data: Dict[str, Any] = None
    output_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.input_data is None:
            self.input_data = {}
        if self.output_data is None:
            self.output_data = {}

class TaskOrchestrator:
    """Orchestrates multi-agent workflows and task execution"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.workflow_templates = self._initialize_templates()
        logger.info("Task Orchestrator initialized")
    
    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize workflow templates"""
        return {
            "email_composition": {
                "name": "Intelligent Email Composition",
                "steps": [
                    {"name": "Initial Draft", "task_type": "email_draft", "target_agent": "MESH"},
                    {"name": "Content Enhancement", "task_type": "writing_assistance", "target_agent": "EmailBot", "dependencies": ["Initial Draft"]},
                    {"name": "Grammar Check", "task_type": "grammar_check", "target_agent": "GrammarBot", "dependencies": ["Content Enhancement"]}
                ]
            },
            "contact_intelligence": {
                "name": "Contact Intelligence Gathering",
                "steps": [
                    {"name": "Basic Contact Info", "task_type": "contact_lookup", "target_agent": "MESH"},
                    {"name": "CRM Enrichment", "task_type": "crm_lookup", "target_agent": "CRMConnector", "dependencies": ["Basic Contact Info"]},
                    {"name": "Profile Synthesis", "task_type": "profile_synthesis", "target_agent": "MESH", "dependencies": ["CRM Enrichment"]}
                ]
            }
        }
    
    async def create_workflow(self, template_name: str, input_data: Dict[str, Any]) -> str:
        """Create a new workflow from template"""
        if template_name not in self.workflow_templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = self.workflow_templates[template_name]
        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        
        steps = []
        for i, step_def in enumerate(template["steps"]):
            step = WorkflowStep(
                step_id=f"step_{i+1}",
                name=step_def["name"],
                task_type=step_def["task_type"],
                target_agent=step_def["target_agent"],
                input_data=input_data,
                dependencies=step_def.get("dependencies", [])
            )
            steps.append(step)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=template["name"],
            steps=steps,
            status=WorkflowStatus.PENDING,
            created_at=datetime.now(),
            input_data=input_data
        )
        
        self.workflows[workflow_id] = workflow
        logger.info(f"Created workflow {workflow_id}")
        return workflow_id
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        
        try:
            step_results = {}
            for step in workflow.steps:
                # Check dependencies
                if not self._check_dependencies(step, step_results):
                    continue
                
                # Execute step
                result = await self._execute_step(step)
                step_results[step.step_id] = result
                
                if not result["success"]:
                    workflow.status = WorkflowStatus.FAILED
                    return {"success": False, "error": result["error"]}
            
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            workflow.output_data = step_results
            
            return {"success": True, "output": step_results}
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            return {"success": False, "error": str(e)}
    
    def _check_dependencies(self, step: WorkflowStep, step_results: Dict[str, Any]) -> bool:
        """Check if step dependencies are satisfied"""
        if not step.dependencies:
            return True
        
        for dep in step.dependencies:
            # Find the step that matches this dependency
            dep_found = False
            for step_id, result in step_results.items():
                if step_id.endswith(dep.lower().replace(" ", "_")):
                    if result.get("success", False):
                        dep_found = True
                        break
            
            if not dep_found:
                return False
        
        return True
    
    async def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step"""
        try:
            # Simulate step execution
            await asyncio.sleep(1)
            
            if step.target_agent == "MESH":
                # Use MESH capabilities
                result = {"success": True, "output": f"MESH executed {step.task_type}"}
            else:
                # Delegate to external agent
                result = await agent_manager.delegate_task(
                    step.task_type, step.target_agent, step.input_data
                )
            
            step.status = "completed"
            step.output_data = result
            return result
            
        except Exception as e:
            step.status = "failed"
            return {"success": False, "error": str(e)}
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status,
            "steps": [{"name": s.name, "status": s.status} for s in workflow.steps]
        }
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """Get available workflow templates"""
        return [
            {"name": name, "display_name": template["name"]}
            for name, template in self.workflow_templates.items()
        ]

# Global instance
task_orchestrator = TaskOrchestrator()

if __name__ == "__main__":
    print("Task Orchestrator Module")
    print("=" * 30)
    
    async def test():
        print("Testing Task Orchestrator...")
        
        templates = task_orchestrator.get_templates()
        print(f"Available templates: {len(templates)}")
        
        if templates:
            workflow_id = await task_orchestrator.create_workflow(
                templates[0]["name"], {"test": "data"}
            )
            
            result = await task_orchestrator.execute_workflow(workflow_id)
            print(f"Execution result: {result}")
        
        print("✅ Test completed!")
    
    asyncio.run(test())
