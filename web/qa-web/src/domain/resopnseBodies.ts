import { TaskPriority, TaskStatus } from "../data/task"

export interface TaskInfo{
    id: string,
    name: string,
    description: string,
    deadline: Date | null,
    create_time: Date,
    redacted_time: Date | null,
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