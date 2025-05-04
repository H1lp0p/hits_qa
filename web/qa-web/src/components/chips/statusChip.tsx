import { TaskStatus } from "../../data/task";
import style from './chip.module.css'

export interface StatusChipProps{
    status: TaskStatus
}

export const StatusChip : React.FC<StatusChipProps> = (prop : StatusChipProps) => {
    const {status} = prop

    return (
        <div className={style.chip}>
            {status}
        </div>
    )
}