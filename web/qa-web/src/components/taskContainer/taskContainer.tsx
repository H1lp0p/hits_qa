import { useDispatch, useSelector } from "react-redux"
import { AppDispatch, StateType } from "../../domain/store"
import { TaskComponent } from "../task/task"
import { TaskInfo } from "../../domain/resopnseBodies"
import { useEffect } from "react"
import { loadData } from "../../domain/thuks"
import { Ordering, OrderingType } from "../../data/pagination"


export const TaskContainer : React.FC = () => {
    const tasks: TaskInfo[] = useSelector((state: StateType) => state.todo.tasks)
    const state = useSelector((state: StateType) => state.todo)
    console.log(state);
    

    const dispatch = useDispatch<AppDispatch>();

    const load = (page: number = 1, page_size: number = 5) => {
        dispatch(loadData({
            page: page,
            pageSize: page_size,
            ordering: Ordering.priority,
            orderingType: OrderingType.asc
        }))
    }

    useEffect(() => {
        load();
    },
        []
    )

    return (
        <div>
        {tasks.length == 0 && <span>No data</span>}
        {tasks.map((it : TaskInfo, ind : number) => <TaskComponent task={it} key={`task_${it.id}_${ind}`}/>)}
        </div>
    )
}