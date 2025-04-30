export enum TaskStatus{

}

export enum TaskPriority{

}

export interface Task{
    id: string,
    name: string,
    describtion: string | null,
}