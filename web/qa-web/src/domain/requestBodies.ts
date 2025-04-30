import { Ordering, OrderingType } from "../data/pagination"
import { TaskPriority } from "../data/task"

export interface CreateTaskModel{
    name: string
    description: string | null
    deadline: Date | null
    priority: TaskPriority | null
}

export interface EditTaskModel{
    name: string | null,
    description: string | null
    deadline: Date | null
    priority: TaskPriority | null,
    done: boolean | null,
}

export interface TaskListQuery{
    ordering: Ordering,
    orderingType: OrderingType,
    page: number,
    pageSize: number,
}