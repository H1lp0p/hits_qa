import { useSelector } from "react-redux"
import { StateType } from "../../domain/store"
import style from './taskEdit.module.css'
import { useEffect, useRef, useState } from "react"
import { CreateTaskModel, EditTaskModel } from "../../domain/requestBodies"
import { TaskPriority, toPriority } from "../../data/task"

export interface TaskEditComponentProps {
    taskId: string | null,
    delTask?: (id: string) => void,
    editTask?: (data: EditTaskModel) => void,
    createTask?: (data: CreateTaskModel) => void
}

export const TaskEditComponent : React.FC<TaskEditComponentProps> = (props: TaskEditComponentProps) => {
    
    const {taskId, createTask, editTask, delTask} = props
    const curTask = useSelector((state: StateType) => taskId ? state.todo.tasks[taskId] : null)

    const nameRef = useRef<HTMLInputElement>(null)
    const descriptionRef = useRef<HTMLTextAreaElement>(null)
    const doneRef = useRef<HTMLInputElement>(null)
    const priorityRef = useRef<HTMLSelectElement>(null)
    const deadlineRef = useRef<HTMLInputElement>(null)

    const [isAllowed, setAllowed] = useState(false);

    useEffect(() => {
        if (nameRef.current){
            nameRef.current.value = curTask? curTask.task.name : ""
            nameRef.current.placeholder = "name"
            nameRef.current.minLength = 4
        }
        if (descriptionRef.current){
            descriptionRef.current.value = curTask ? (curTask.task.description ? curTask.task.description : "") : ""
            descriptionRef.current.placeholder = "description"
        }
        if (doneRef.current){
            doneRef.current.checked = curTask?.task.done || false
        }
        if (priorityRef.current){
            priorityRef.current.value = curTask?.task.priority.toString() || "-1"
        }
        if (deadlineRef.current){
            deadlineRef.current.value = curTask?.task.deadline || ""
        }
    }, [curTask])



    const handleCreate = () => {
        if (createTask){
            if (nameRef.current && descriptionRef.current && doneRef.current && priorityRef.current && deadlineRef.current){
                createTask({
                    name : nameRef.current.value,
                    description : descriptionRef.current.value || null,
                    deadline: deadlineRef.current.value || null,
                    priority: priorityRef.current.value != "-1" ? toPriority(priorityRef.current.value) : null
                })
            }
        }
    }

    const handleEdit = () => {
        if (editTask) {
            if (curTask && nameRef.current && descriptionRef.current && doneRef.current && priorityRef.current && deadlineRef.current){
                var result_priority = priorityRef.current.value != "-1" && toPriority(priorityRef.current.value) != curTask.task.priority ? toPriority(priorityRef.current.value) : null
                
                if (priorityRef.current.value != "-1" && toPriority(priorityRef.current.value) != curTask.task.priority){
                    console.log(priorityRef.current.value, curTask.task.priority);
                    
                }
                
                editTask({
                    name: nameRef.current.value != curTask.task.name ? nameRef.current.value : null,
                    description: descriptionRef.current.value != curTask.task.description ? descriptionRef.current.value : null,
                    deadline: deadlineRef.current.value != curTask.task.deadline && deadlineRef.current.value.length > 0 ? deadlineRef.current.value : null,
                    priority: priorityRef.current.value != "-1" && toPriority(priorityRef.current.value) != curTask.task.priority ? toPriority(priorityRef.current.value) : null,
                    done: doneRef.current.checked != curTask.task.done ? doneRef.current.checked : null,
                })
            }
        }
    }

    const handleDelete = () => {
        if (delTask && taskId){
            delTask(taskId)
        }
    }

    const validationHandler = () => {
        var newAllowed = false
        if (taskId){
            if (curTask && nameRef.current && descriptionRef.current && doneRef.current && priorityRef.current && deadlineRef.current){
                newAllowed = nameRef.current.value !== curTask.task.name ||
                descriptionRef.current.value !== normalize(curTask.task.description) ||
                deadlineRef.current.value !== normalize(curTask.task.deadline) ||
                toPriority(priorityRef.current.value) !== curTask.task.priority || 
                doneRef.current.checked !== curTask.task.done;
            }
                
        }
        else{
            if (nameRef.current && descriptionRef.current && doneRef.current && priorityRef.current && deadlineRef.current){
                newAllowed = nameRef.current.value.length >= 4
            }
        }
        setAllowed(newAllowed)
    }

    return (
        <div className={style.taskEdit}>
            <input type="text" ref={nameRef} name="name" onChange={() => validationHandler()}/>
            <textarea ref={descriptionRef} name="description" onChange={() => validationHandler()}/>
            <div style={{display:'inline', textAlign: "start"}}>
                <label htmlFor="input_done">Done?</label>
                <input id="input_done" type="checkbox" name="done" ref={doneRef} onChange={() => validationHandler()}></input>
            </div>
            <select name="priority" ref={priorityRef} onChange={() => validationHandler()}>
                <option value={-1}>-</option>
                <option value={3}>low</option>
                <option value={2}>medium</option>
                <option value={1}>high</option>
                <option value={0}>critical</option>
            </select>
            <input type="date" name="deadline" ref={deadlineRef} onChange={() => validationHandler()}></input>

            {taskId && 
                <div style={{display: "flex", flexDirection: "column"}}>
                    <button onClick={() => handleEdit()} disabled={!isAllowed}>Edit</button>
                    <button onClick={() => handleDelete()}>Delete</button>
                </div>
            }
            {!taskId && 
                <button onClick={() => handleCreate()} disabled={!isAllowed}>Create</button>
            }
        </div>
    )
}

const normalize = (val: string | null | undefined) => val ?? "";