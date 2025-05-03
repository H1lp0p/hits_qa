import { useSelector } from 'react-redux'
import { TaskInfo } from '../../domain/resopnseBodies'
import { State, StateType, TaskState } from '../../domain/store'
import style from './task.module.css'

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
    if (deadlineDate){
        isFire = deadlineDate.getHours() - (new Date()).getHours() < 24 * 3
    }

    const select = (e: React.MouseEvent<HTMLDivElement>) => {
        e.stopPropagation()
        
        props.selectFunc && taskId? props.selectFunc(taskId) : null
    }

    return (
        <div className={`${style.task} ${props.selected ? style.selected : ""} ${isFire ? style.fire : ""}`} onClick={select}>
            <span>
                {`${task?.task.name}`}
            </span>
            <span>
                {`${task?.task.description ? task.task.description : "no description"}`}
            </span>
            {deadlineDate && <span>
                {`to ${deadlineDate ? getDateString(deadlineDate): "no deadline"}`}
            </span>}
        </div>
    )
}

const getDateString = (date: Date) => {
    return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
}