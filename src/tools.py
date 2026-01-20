from datetime import datetime, date
from typing import Optional, List, Dict, Any
from .auth import get_service

def is_due_today_or_overdue(due_date: str) -> bool:
    if not due_date:
        return False
    # RFC 3339 format e.g. 2024-12-25T00:00:00.000Z or similar
    # Python's fromisoformat might handle it depending on Z
    try:
        # Simple string handling for now as Google returns RFC 3339
        dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        due = dt.date()
        today = date.today()
        return due <= today
    except ValueError:
        return False

def format_task(task: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": task.get("id"),
        "title": task.get("title"),
        "notes": task.get("notes"),
        "due": task.get("due"),
        "status": task.get("status"),
        "completed": task.get("completed"),
        "updated": task.get("updated")
    }

def get_default_task_list_id(service) -> str:
    results = service.tasklists().list(maxResults=1).execute()
    items = results.get('items', [])
    if not items:
        raise ValueError("No task lists found.")
    return items[0]['id']

def register_tools(mcp):
    
    @mcp.tool()
    def list_task_lists() -> str:
        """List all task lists."""
        service = get_service()
        results = service.tasklists().list(maxResults=100).execute()
        items = results.get('items', [])
        return str(items) # Return JSON string or object depending on FastMCP behavior. FastMCP handles Dict.
        # Better to return List[Dict]

    # Re-defining to return structured data
    @mcp.tool()
    def get_task_lists() -> List[Dict[str, Any]]:
        """Retrieve all task lists."""
        service = get_service()
        results = service.tasklists().list(maxResults=100).execute()
        return results.get('items', [])

    @mcp.tool()
    def create_task(title: str, notes: Optional[str] = None, due: Optional[str] = None, task_list_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new task in Google Tasks.
        
        Args:
            title: Title of the new task.
            notes: Notes/description for the task.
            due: Due date in RFC 3339 format (e.g. 2024-12-25T15:00:00Z). 
                 Note: The Google Tasks API discards time information in the 'due' field. 
                 This tool automatically appends the time to the notes field if provided.
            task_list_id: The ID of the task list. If not provided, uses default.
        """
        service = get_service()
        if not task_list_id:
            task_list_id = get_default_task_list_id(service)
            
        body = {"title": title}
        if notes:
            body["notes"] = notes
        if due:
            body["due"] = due
            
        result = service.tasks().insert(tasklist=task_list_id, body=body).execute()
        return {
            "success": True, 
            "message": f"Task '{result.get('title')}' created successfully.",
            "task": format_task(result)
        }

    @mcp.tool()
    def get_current_tasks(task_list_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve all tasks that are due today or overdue, as well as tasks with no due date."""
        service = get_service()
        if not task_list_id:
            task_list_id = get_default_task_list_id(service)
            
        # showCompleted=False by default in JS implementation used here
        results = service.tasks().list(tasklist=task_list_id, showCompleted=False, showHidden=False, maxResults=100).execute()
        all_tasks = results.get('items', [])
        
        relevant_tasks = [t for t in all_tasks if t.get('status') != 'completed'] # Double check, API filters it too
        
        today = date.today()
        
        final_overdue = []
        final_due_today = []
        final_no_due = []
        
        for task in relevant_tasks:
            due_str = task.get('due')
            if not due_str:
                final_no_due.append(format_task(task))
                continue
            
            try:
                dt = datetime.fromisoformat(due_str.replace('Z', '+00:00'))
                due_d = dt.date()
                if due_d < today:
                    final_overdue.append(format_task(task))
                elif due_d == today:
                    final_due_today.append(format_task(task))
                # Future tasks are ignored
            except ValueError:
                pass
                
        return {
            "task_list_id": task_list_id,
            "overdue": final_overdue,
            "due_today": final_due_today,
            "no_due_date": final_no_due,
            "summary": {
                "overdue_count": len(final_overdue),
                "due_today_count": len(final_due_today),
                "no_due_date_count": len(final_no_due),
                "total": len(final_overdue) + len(final_due_today) + len(final_no_due)
            }
        }

    @mcp.tool()
    def update_task(task_id: str, task_list_id: Optional[str] = None, title: Optional[str] = None, notes: Optional[str] = None, status: Optional[str] = None, due: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing task."""
        service = get_service()
        if not task_list_id:
            task_list_id = get_default_task_list_id(service)
            
        body = {}
        if title: body['title'] = title
        if notes: body['notes'] = notes
        if status: body['status'] = status
        if due: body['due'] = due
        
        result = service.tasks().patch(tasklist=task_list_id, task=task_id, body=body).execute()
        return {
            "success": True,
            "message": "Task updated successfully",
            "task": format_task(result)
        }

    @mcp.tool()
    def delete_task(task_id: str, task_list_id: Optional[str] = None) -> Dict[str, Any]:
        """Delete a task."""
        service = get_service()
        if not task_list_id:
            task_list_id = get_default_task_list_id(service)
            
        service.tasks().delete(tasklist=task_list_id, task=task_id).execute()
        return {"success": True, "message": "Task deleted successfully"}

    @mcp.tool()
    def search_tasks(query: str) -> List[Dict[str, Any]]:
        """Search for tasks matching a query string (Note: Google Tasks API doesn't support full text search efficiently, this performs client-side filtering on recent tasks)."""
        # JS implementation scans all tasks?
        # JS 'search-tasks.ts' iterates over all task lists, gets all tasks, and filters by title/notes includes query.
        service = get_service()
        
        task_lists_result = service.tasklists().list(maxResults=10).execute()
        task_lists = task_lists_result.get('items', [])
        
        found_tasks = []
        for tl in task_lists:
            # Limit to 100 per list for performance
            tasks_res = service.tasks().list(tasklist=tl['id'], maxResults=100, showCompleted=True, showHidden=True).execute()
            items = tasks_res.get('items', [])
            for item in items:
                title = item.get('title', '').lower()
                notes = item.get('notes', '').lower()
                q = query.lower()
                if q in title or q in notes:
                    ft = format_task(item)
                    ft['task_list_title'] = tl['title']
                    found_tasks.append(ft)
                    
        return found_tasks

