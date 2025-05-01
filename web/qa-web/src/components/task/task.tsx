import { TaskInfo } from '../../domain/resopnseBodies'
import style from './task.module.css'

export interface TaskComponentProps{
    task: TaskInfo
}

export const TaskComponent : React.FC<TaskComponentProps> = (props: TaskComponentProps) => {
    
    const {task} = props

    return (
        <div className={style.task}>
            {
                task.name
            }
        </div>
    )
}