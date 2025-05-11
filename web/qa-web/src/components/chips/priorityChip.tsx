import { TaskPriority } from "../../data/task"
import style from './chip.module.css'

export interface PriorityChipProps{
    priority: TaskPriority
}

export const PriorityChip : React.FC<PriorityChipProps> = (prop: PriorityChipProps) => {
    const {priority} = prop

    const priorityNaming = ["critical", "high", "medium", "low"]

    const priorityString = priorityNaming[priority]

    return (
        <div className={style.chip}>
            {priorityString}
        </div>
    )
}