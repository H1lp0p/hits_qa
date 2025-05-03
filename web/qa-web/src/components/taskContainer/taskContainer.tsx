import { useDispatch, useSelector } from "react-redux"
import { AppDispatch, StateType, TaskState } from "../../domain/store"
import { TaskComponent } from "../task/task"
import { TaskInfo } from "../../domain/resopnseBodies"
import { useEffect, useState } from "react"
import { loadData, createTask, deleteTask, editTask } from "../../domain/thuks"
import { Ordering, OrderingType } from "../../data/pagination"
import { CreateTaskModel, EditTaskModel } from "../../domain/requestBodies"
import { TaskEditComponent } from "../taskEdit/taskEdit"


export const TaskContainer : React.FC = () => {
    const {tasks, pagination, ordering, orderingType, error, dataState} = useSelector((state: StateType) => state.todo)

    const [currentChoosedId, setCurrentChoosedId] = useState<string | null>(null);

    const dispatch = useDispatch<AppDispatch>();

    const load = (page: number = 1, page_size: number = 5, ordering = Ordering.priority, orderingType = OrderingType.asc) => {
        dispatch(loadData({
            page: page,
            pageSize: page_size,
            ordering: ordering,
            orderingType: orderingType
        }))
    }

    const create = (data: CreateTaskModel) => {
        dispatch(createTask(data))
    }

    const del = (id: string) => {
        if (currentChoosedId){
            dispatch(deleteTask({id: id}))
        }
    }

    const edit = (data: EditTaskModel) => {
        if (currentChoosedId){
            dispatch(editTask({editData: data, id: currentChoosedId}))
        }
    }

    const nextPage = () => {
        if (pagination.items_count > pagination.page_size * pagination.page){
            dispatch(loadData({
                page: pagination.page + 1,
                pageSize: pagination.page_size,
                ordering: ordering,
                orderingType: orderingType,
            }))
            setCurrentChoosedId(null)
        }
    }

    const prewPage = () => {
        if (pagination.page > 1){
            dispatch(loadData({
                page: pagination.page - 1,
                pageSize: pagination.page_size,
                ordering: ordering,
                orderingType: orderingType,
            }))
            setCurrentChoosedId(null)
        }
    }

    const select = (id: string) => {
        setCurrentChoosedId(id == currentChoosedId ? null: id)
    }

    useEffect(() => {
        load();
    },
        []
    )

    return (
        <div>
            <div>
                <button onClick={() => prewPage()}>Prew</button>
                <span>{pagination.page}</span>
                <button onClick={() => nextPage()}>Next</button>
            </div>
            <div style={{display: "flex", flexDirection: "row"}}>
                <div>
                    {Object.keys(tasks).length == 0 && <span>No data</span>}
                    {Object.keys(tasks).map((it : string, ind : number) => 
                        <TaskComponent 
                            taskId={it}
                            selected={it == currentChoosedId}
                            selectFunc={select}
                            key={`task_${it}_${ind}`}
                        />
                    )}
                </div>
                <div>
                    <TaskEditComponent 
                        taskId={currentChoosedId}
                        delTask={del}
                        editTask={edit}
                        createTask={create}
                    />
                </div>
            </div>
        </div>
    )
}