export enum TaskStatus{
    active = "active",
    completed = "completed",
    overdue = "overdue",
    late = "late",
}

export enum TaskPriority{
    low = 0,
    medium = 1,
    high = 2,
    critical = 3,
}

export const toPriority = (st: string) => {
    console.log("!priority mapper", st);
    
    switch(st){
        case "0": return TaskPriority.low;
        case "1": return TaskPriority.medium;
        case "2": return TaskPriority.high;
        case "3": return TaskPriority.critical;
    }
    return TaskPriority.medium
}

export interface Task{
    id: string,
    name: string,
    description: string | null,
    deadline: string | null,
    create_time: string,
    redacted_time: string | null,
    status: TaskStatus,
    priority: TaskPriority,
    done: boolean,
}