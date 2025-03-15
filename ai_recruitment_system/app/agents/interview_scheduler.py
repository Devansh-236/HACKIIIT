from typing import Dict, List, Any, Optional
import datetime
from moya.agents.base_agent import Agent, AgentConfig
from moya.tools.base_tool import BaseTool

class InterviewSchedulerTool(BaseTool):
    """Tool for scheduling interviews and managing interview slots"""
    
    name = "interview_scheduler"
    description = "Schedules interviews and manages available interview slots"
    function = "schedule_interview"
    
    def __init__(self):
        """Initialize the interview scheduler tool"""
        super().__init__(name=self.name, function=self.function)
        self.scheduled_interviews = []
    
    def schedule_interview(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule an interview based on candidate and job information
        
        Args:
            data: Dictionary containing:
                - candidate_info: Information about the candidate
                - job_info: Information about the job
                - selected_slot: The chosen interview slot
                
        Returns:
            Interview confirmation details
        """
        candidate_info = data.get("candidate_info", {})
        job_info = data.get("job_info", {})
        selected_slot = data.get("selected_slot", {})
        
        # Validate required fields
        if not candidate_info.get("name"):
            return {"error": "Candidate name is required"}
        
        if not job_info.get("title") or not job_info.get("job_id"):
            return {"error": "Job details are required"}
            
        if not selected_slot.get("date") or not selected_slot.get("time"):
            return {"error": "Valid interview slot is required"}
        
        # Create interview record
        interview_id = f"INT-{len(self.scheduled_interviews) + 1:03d}"
        
        # Format date for display
        interview_date = selected_slot.get("date", "")
        interview_time = selected_slot.get("time", "")
        
        try:
            date_obj = datetime.datetime.strptime(f"{interview_date} {interview_time}", "%Y-%m-%d %H:%M")
            formatted_date = date_obj.strftime("%A, %B %d, %Y")
            formatted_time = date_obj.strftime("%I:%M %p")
        except ValueError:
            formatted_date = interview_date
            formatted_time = interview_time
        
        interview = {
            "interview_id": interview_id,
            "candidate": {
                "name": candidate_info.get("name"),
                "email": candidate_info.get("contact_info", {}).get("email"),
                "phone": candidate_info.get("contact_info", {}).get("phone")
            },
            "job": {
                "title": job_info.get("title"),
                "job_id": job_info.get("job_id"),
                "company": job_info.get("company"),
                "department": job_info.get("department")
            },
            "schedule": {
                "date": interview_date,
                "time": interview_time,
                "formatted_date": formatted_date,
                "formatted_time": formatted_time,
                "interviewer": selected_slot.get("interviewer"),
                "location": selected_slot.get("location")
            },
            "status": "scheduled",
            "created_at": datetime.datetime.now().isoformat()
        }
        
        # Add interview to scheduled list
        self.scheduled_interviews.append(interview)
        
        # Create confirmation message for output
        confirmation = {
            "interview_id": interview_id,
            "message": f"Interview scheduled successfully for {candidate_info.get('name')}",
            "details": {
                "candidate": candidate_info.get("name"),
                "position": job_info.get("title"),
                "company": job_info.get("company"),
                "date": formatted_date,
                "time": formatted_time,
                "interviewer": selected_slot.get("interviewer"),
                "location": selected_slot.get("location")
            },
            "status": "scheduled",
            "next_steps": [
                "Confirmation email will be sent to the candidate",
                "Calendar invitation will be sent to all participants",
                "Candidate should prepare for a technical assessment"
            ]
        }
        
        return confirmation
    
    def get_available_slots(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get available interview slots for a job
        
        Args:
            data: Dictionary containing:
                - job_id: ID of the job to get slots for
                
        Returns:
            List of available interview slots
        """
        job_id = data.get("job_id")
        
        if not job_id:
            return {"error": "Job ID is required"}
        
        # In a real system, this would fetch slots from a database
        # For this demo, we'll just return mock data
        return {
            "job_id": job_id,
            "available_slots": data.get("job_info", {}).get("interview_slots", [])
        }


class InterviewSchedulerAgent(Agent):
    """Agent for scheduling interviews and managing the interview process"""
    
    def __init__(self, config: AgentConfig = None):
        """Initialize the interview scheduler agent"""
        if config is None:
            config = AgentConfig(
                agent_name="interview_scheduler",
                agent_type="interview_scheduler",
                description="Schedules and manages the interview process",
                system_prompt="You are an interview scheduling assistant that helps coordinate interviews between candidates and hiring managers."
            )
        super().__init__(config)
        self.scheduler_tool = InterviewSchedulerTool()
    
    async def handle_message(self, message: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Handle interview scheduling requests
        
        Args:
            message: Dictionary containing scheduling request details
                
        Returns:
            Scheduling confirmation or error message
        """
        try:
            # Validate the input message
            if not isinstance(message, dict):
                return {"error": "Message must be a dictionary"}
            
            action = message.get("action", "schedule")
            
            if action == "schedule":
                # Schedule an interview
                if "candidate_info" not in message:
                    return {"error": "Message must contain candidate_info"}
                    
                if "job_info" not in message:
                    return {"error": "Message must contain job_info"}
                    
                if "selected_slot" not in message:
                    return {"error": "Message must contain selected_slot"}
                
                return self.scheduler_tool.schedule_interview(message)
                
            elif action == "get_slots":
                # Get available slots
                if "job_id" not in message or "job_info" not in message:
                    return {"error": "Message must contain job_id and job_info"}
                
                return self.scheduler_tool.get_available_slots(message)
                
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            return {"error": f"Failed to process scheduler request: {str(e)}"}
    
    async def handle_message_stream(self, message: str, **kwargs):
        """Stream is not supported for interview scheduling"""
        yield "Streaming is not supported for interview scheduling. Please use handle_message instead."


# Helper function for standalone use
async def schedule_interview(candidate_info: Dict[str, Any], job_info: Dict[str, Any], 
                           selected_slot: Dict[str, Any]) -> Dict[str, Any]:
    """Schedule an interview for a candidate
    
    Args:
        candidate_info: Information about the candidate
        job_info: Information about the job
        selected_slot: The chosen interview slot
        
    Returns:
        Interview confirmation details
    """
    config = AgentConfig(
        agent_name="interview_scheduler",
        agent_type="interview_scheduler",
        description="Schedules and manages the interview process",
        system_prompt="You are an interview scheduling assistant that helps coordinate interviews between candidates and hiring managers."
    )
    agent = InterviewSchedulerAgent(config)
    
    return await agent.handle_message({
        "action": "schedule",
        "candidate_info": candidate_info,
        "job_info": job_info,
        "selected_slot": selected_slot
    })


async def get_available_slots(job_id: str, job_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get available interview slots for a job
    
    Args:
        job_id: ID of the job to get slots for
        job_info: Information about the job
        
    Returns:
        List of available interview slots
    """
    config = AgentConfig(
        agent_name="interview_scheduler",
        agent_type="interview_scheduler",
        description="Schedules and manages the interview process",
        system_prompt="You are an interview scheduling assistant that helps coordinate interviews between candidates and hiring managers."
    )
    agent = InterviewSchedulerAgent(config)
    
    return await agent.handle_message({
        "action": "get_slots",
        "job_id": job_id,
        "job_info": job_info
    })
