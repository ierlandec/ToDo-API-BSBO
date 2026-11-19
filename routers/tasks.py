from fastapi import APIRouter, HTTPException, Query, Response, status
from database import tasks_db
from datetime import datetime
from schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)


@router.get("") 
async def get_all_tasks() -> dict: 
    return { 
        "count": len(tasks_db),  # считает количество записей в хранилище 
        "tasks": tasks_db # выводит всё, чта есть в хранилище 
    } 
 
@router.get("/quadrant/{quadrant}") 
async def get_tasks_by_quadrant(quadrant: str) -> dict: 
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]: 
        raise HTTPException(    #специальный класс в FastAPI для возврата HTTP ошибок. Не забудьте добавть его вызов в 1 строке 
            status_code=400, 
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4"  #текст, который будет выведен пользователю   
        ) 
    
    filtered_tasks = [ 
        task                          # ЧТО добавляем в список 
        for task in tasks_db          # ОТКУДА берем элементы 
        if task["quadrant"] == quadrant  # УСЛОВИЕ фильтрации 
    ] 
    
    return { 
        "quadrant": quadrant, 
        "count": len(filtered_tasks), 
        "tasks": filtered_tasks 
}


@router.get("/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    if status not in ("completed", "pending"):
        raise HTTPException(
            status_code=404,
            detail="Неизвестный статус. Используйте completed или pending.",
        )

    is_completed = status == "completed"
    tasks = [task for task in tasks_db if task["completed"] == is_completed]
    return {"status": status, "count": len(tasks), "tasks": tasks}


@router.get("/search")
async def search_tasks(q: str = Query(min_length=2)) -> dict:
    keyword = q.casefold()
    tasks = [
        task
        for task in tasks_db
        if keyword in task["title"].casefold()
        or keyword in (task.get("description") or "").casefold()
    ]
    return {"query": q, "count": len(tasks), "tasks": tasks}


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: int) -> TaskResponse:
    for task in tasks_db:
        if task["id"] == task_id:
            return task

    raise HTTPException(status_code=404, detail="Задача не найдена.")
 
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED) 
async def create_task(task: TaskCreate) -> TaskResponse: 
   
    if task.is_important and task.is_urgent: 
        quadrant = "Q1" 
    elif task.is_important and not task.is_urgent: 
        quadrant = "Q2" 
    elif not task.is_important and task.is_urgent: 
        quadrant = "Q3" 
    else: 
        quadrant = "Q4" 
 
    new_id = max([t["id"] for t in tasks_db], default=0) + 1
    
    new_task = { 
        "id": new_id, 
        "title": task.title, 
        "description": task.description, 
        "is_important": task.is_important, 
        "is_urgent": task.is_urgent, 
        "quadrant": quadrant, 
        "completed": False, 
        "created_at": datetime.now() 
    } 
 
    tasks_db.append(new_task)
    
    return new_task 

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate) -> TaskResponse:
    task = next(
        (task for task in tasks_db if task["id"] == task_id),
        None,
    )
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        task[field] = value

    if "is_important" in update_data or "is_urgent" in update_data:
        if task["is_important"] and task["is_urgent"]:
            task["quadrant"] = "Q1"
        elif task["is_important"] and not task["is_urgent"]:
            task["quadrant"] = "Q2"
        elif not task["is_important"] and task["is_urgent"]:
            task["quadrant"] = "Q3"
        else:
            task["quadrant"] = "Q4"
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_task(task_id: int): 
    task = next(( 
        task for task in tasks_db 
        if task["id"] == task_id), 
        None 
    ) 
    if not task: 
        raise HTTPException(status_code=404, detail="Задача не найдена") 
 
    tasks_db.remove(task) 
    
    return Response(status_code=status.HTTP_204_NO_CONTENT) 