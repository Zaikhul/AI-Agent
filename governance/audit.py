"""
Governance and audit trail management
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class AuditTrail:
    """Audit trail for all agent operations"""
    
    def __init__(self, audit_dir: str = "audit"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(exist_ok=True)
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = self.audit_dir / f"session_{self.current_session}.jsonl"
    
    def record_event(self, event_type: str, **data):
        """Record an audit event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "session": self.current_session,
            "event_type": event_type,
            **data
        }
        
        with open(self.session_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def record_agent_action(self, agent_name: str, action: str, input_data: Any, output_data: Any):
        """Record agent action"""
        self.record_event(
            "agent_action",
            agent=agent_name,
            action=action,
            input=str(input_data)[:500],  # Truncate for storage
            output=str(output_data)[:500]
        )
    
    def record_escalation(self, reason: str, context: Dict):
        """Record manual escalation"""
        self.record_event(
            "manual_escalation",
            reason=reason,
            context=context,
            requires_human_review=True
        )
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        if not self.session_file.exists():
            return {}
        
        events = []
        with open(self.session_file, 'r') as f:
            for line in f:
                events.append(json.loads(line))
        
        return {
            "session_id": self.current_session,
            "total_events": len(events),
            "event_types": list(set(e["event_type"] for e in events)),
            "events": events
        }

# Global audit instance
audit_trail = AuditTrail()