"""
entry point with all features integrated
"""
import asyncio
import sys
from typing import Optional

# Initialize global components
config_manager = ConfigManager()
provider_manager = ProviderManager(config_manager)

print("=== Enhanced AI Coding Agent System ===")
print(f"Config Version: {config_manager.config_version}")
print(f"Observability: Enabled")
print(f"Audit Trail: Enabled")
print(f"Available Providers: {list(provider_manager.providers.keys())}")
print("=" * 50)

async def execute_agent_task(task_description: str):
    """Execute a coding task with full observability and error handling"""
    
    trace_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    observability.start_trace(trace_id, "coding_task", task=task_description)
    
    audit_trail.record_event("task_start", task=task_description)
    
    try:
        # Phase 1: Architecture Design
        print("\n[1/4] Architecture Design Phase...")
        messages = [
            {"role": "system", "content": "You are a software architect."},
            {"role": "user", "content": f"Design architecture for: {task_description}"}
        ]
        
        design_result = await provider_manager.call_with_fallback(
            primary_provider="gpt_config",
            fallback_providers=["glm_config"],
            messages=messages
        )
        
        if not design_result["success"]:
            observability.log_error("design_failed", design_result["error"])
            audit_trail.record_escalation("Design phase failed", design_result)
            print("❌ Design phase failed - escalating to human review")
            return
        
        print(f"✓ Design complete ({design_result['duration']:.2f}s, {design_result['provider']})")
        audit_trail.record_agent_action("Architect", "design", task_description, design_result["content"])
        
        # Phase 2: Implementation
        print("\n[2/4] Implementation Phase...")
        messages = [
            {"role": "system", "content": "You are an expert Python developer."},
            {"role": "user", "content": f"Implement this design:\\n\\n{design_result['content']}"}
        ]
        
        code_result = await provider_manager.call_with_fallback(
            primary_provider="coding_config",
            fallback_providers=["gpt_config"],
            messages=messages
        )
        
        if not code_result["success"]:
            observability.log_error("implementation_failed", code_result["error"])
            audit_trail.record_escalation("Implementation phase failed", code_result)
            print("❌ Implementation phase failed - escalating to human review")
            return
        
        print(f"✓ Implementation complete ({code_result['duration']:.2f}s)")
        audit_trail.record_agent_action("Developer", "implement", design_result["content"], code_result["content"])
        
        # Phase 3: Code Review
        print("\n[3/4] Code Review Phase...")
        messages = [
            {"role": "system", "content": "You are a code reviewer."},
            {"role": "user", "content": f"Review this code:\\n\\n{code_result['content']}"}
        ]
        
        review_result = await provider_manager.call_with_fallback(
            primary_provider="glm_config",
            fallback_providers=["gpt_config"],
            messages=messages
        )
        
        if review_result["success"]:
            print(f"✓ Review complete ({review_result['duration']:.2f}s)")
            audit_trail.record_agent_action("Reviewer", "review", code_result["content"], review_result["content"])
        
        # Phase 4: Summary
        print("\n[4/4] Task Summary")
        print("=" * 50)
        print("✓ All phases completed successfully")
        
        # Export metrics
        metrics_summary = observability.metrics.get_stats("api_call_duration")
        if metrics_summary:
            print(f"\\nPerformance Metrics:")
            print(f"  Total API calls: {metrics_summary['count']}")
            print(f"  Avg duration: {metrics_summary['avg']:.2f}s")
            print(f"  Total time: {metrics_summary['sum']:.2f}s")
        
        observability.end_trace(trace_id, success=True)
        audit_trail.record_event("task_complete", success=True)
        
        return {
            "design": design_result["content"],
            "code": code_result["content"],
            "review": review_result.get("content", "Not available")
        }
    
    except Exception as e:
        observability.log_error("task_execution_failed", str(e))
        observability.end_trace(trace_id, success=False, error=str(e))
        audit_trail.record_event("task_failed", error=str(e))
        print(f"\\n❌ Task execution failed: {e}")
        raise

async def main():
    """Main entry point"""
    
    # Example task
    task = """
    Create a Python class for a REST API client with:
    - GET, POST, PUT, DELETE methods
    - Retry logic with exponential backoff
    - Comprehensive error handling
    - Type hints and docstrings
    """
    
    print(f"\\nTask: {task}\\n")
    
    try:
        result = await execute_agent_task(task)
        
        if result:
            print("\\n" + "=" * 50)
            print("CODE GENERATED:")
            print("=" * 50)
            print(result["code"][:500] + "..." if len(result["code"]) > 500 else result["code"])
    
    except KeyboardInterrupt:
        print("\\n\\nTask interrupted by user")
        audit_trail.record_event("user_interrupt")
    
    except Exception as e:
        print(f"\\nFatal error: {e}")
        sys.exit(1)
    
    finally:
        # Export final metrics and audit
        print("\\n" + "=" * 50)
        print("Session Summary:")
        print("=" * 50)
        
        metrics_export = observability.metrics.export_metrics()
        audit_summary = audit_trail.get_session_summary()
        
        print(f"Total events logged: {audit_summary.get('total_events', 0)}")
        print(f"Metrics tracked: {len(metrics_export)}")
        print(f"\\nAudit trail: {audit_trail.session_file}")
        print(f"Logs directory: logs/")

if __name__ == "__main__":
    asyncio.run(main())
