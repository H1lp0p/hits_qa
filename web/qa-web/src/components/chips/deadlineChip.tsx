import style from './chip.module.css'

export interface DeadlineChipProps{
    deadline: Date | string | number
}

export const DeadlineChip : React.FC<DeadlineChipProps> = (prop: DeadlineChipProps) => {
    const {deadline} = prop

    const date = new Date(deadline)

    return(
        <div className={style.chip}>
            to {date.toISOString().substring(0,10)}
        </div>
    )
}