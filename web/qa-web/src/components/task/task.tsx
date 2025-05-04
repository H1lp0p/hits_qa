import { useSelector } from 'react-redux'
import { TaskInfo } from '../../domain/resopnseBodies'
import { State, StateType, TaskState } from '../../domain/store'
import style from './task.module.css'
import { DeadlineChip } from '../chips/deadlineChip'
import { PriorityChip } from '../chips/priorityChip'
import { StatusChip } from '../chips/statusChip'

export interface TaskComponentProps{
    taskId?: string,
    selected?: boolean,
    selectFunc?: (id: string) => void
}

export const TaskComponent : React.FC<TaskComponentProps> = (props: TaskComponentProps) => {
    
    const {taskId} = props

    const task = useSelector((state : StateType) => taskId ? state.todo.tasks[taskId] : undefined)

    const deadline = task?.task.deadline
    const deadlineDate = deadline? new Date(deadline) : null

    var isFire = false
    var outdated = false
    if (deadlineDate){
        const diff = (deadlineDate.getTime() - (new Date()).getTime())
        isFire = diff < 3 * 24 * 60 * 60 * 1000
        outdated = diff < 0 && ! task!.task.done
    }

    const colorClass = task?.task.done ? "" : (outdated ? style.outdated : (isFire ? style.fire : ""))  

    const select = (e: React.MouseEvent<HTMLDivElement>) => {
        e.stopPropagation()
        
        props.selectFunc && taskId? props.selectFunc(taskId) : null
    }

    return (
        <div className={`${style.task} ${props.selected ? style.selected : ""} ${colorClass}`} onClick={select}>
            <span>
                {`${task?.task.name}`}
            </span>
            <span>
                {`${task?.task.description ? task.task.description : ""}`}
            </span>
            <div style={{display: "flex", flexDirection: "row", justifyContent: "center"}}>
                {task && <PriorityChip priority={task.task.priority}/>}
                {task && <StatusChip status={task.task.status}/>}
                {deadline && <DeadlineChip deadline={deadline}/>}
            </div>
        </div>
    )
}

const getDateString = (date: Date) => {
    return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
}