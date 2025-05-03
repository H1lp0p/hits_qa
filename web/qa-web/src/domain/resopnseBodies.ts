import { TaskPriority, TaskStatus } from "../data/task"

export interface TaskInfo{
    id: string,
    name: string,
    description: string,
    deadline: string | null,
    create_time: string,
    redacted_time: string | null,
    status: TaskStatus,
    priority: TaskPriority,
    done: boolean,
}

export interface Pagination{
    items_count: number,
    page: number,
    page_size: number,
}

export interface TaskList{
    tasks: TaskInfo[],
    pagination: Pagination
}