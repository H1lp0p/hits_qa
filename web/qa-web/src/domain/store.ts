import { configureStore, createReducer, createSlice } from "@reduxjs/toolkit";
import { createTask, deleteTask, editTask, loadData } from "./thuks";
import { Pagination } from "./resopnseBodies";
import { Task, TaskPriority, TaskStatus } from "../data/task";
import { Ordering, OrderingType } from "../data/pagination";

export interface TaskState{
    task: Task,
    dataState: "loading" | "error" | "success",
    error: string | null,
}

export interface State {
    tasks: Record<string, TaskState>,
    pagination: Pagination,
    ordering: Ordering,
    orderingType: OrderingType
    dataState: "loading" | "error" | "success",
    error: string | null,
}

const initState: State = {
    tasks : {},
    pagination: {
        page: 1,
        page_size: 5,
        items_count: 0,
    },
    ordering: Ordering.priority,
    orderingType: OrderingType.desc,
    dataState: "success",
    error: null
}

export const slice = createSlice({
    name: "todo",
    initialState: initState,
    reducers: {},
    extraReducers: (builder) => {
        //configuring loading actions
        builder.addCase(loadData.pending, (state) => {
            state.dataState = "loading",
            state.error = null
        })
        builder.addCase(loadData.fulfilled, (state, action) => {
            state.dataState = "success",
            state.tasks = action.payload.tasks.reduce((accum, task) => {
                accum[task.id] = {
                    task: task,
                    dataState: "success"
                } as TaskState
                return accum
            }, {} as Record<string, TaskState>)
            state.pagination = action.payload.pagination
        })
        builder.addCase(loadData.rejected, (state, action) => {
            state.dataState = "error"
            state.error = action.error.message || "Unknown error"
        })
        //configuring creating actions
        builder.addCase(createTask.pending, (state, action) => {
            state.tasks["new_task"] = {
                task: {
                    id: "new_task",
                    ...action.meta.arg,
                    create_time: Date().toString(),
                    redacted_time: null,
                    status: TaskStatus.active,
                    priority: TaskPriority.medium,
                    done: false
                },
                dataState: "loading",
                error: null
            }
        })
        builder.addCase(createTask.fulfilled, (state, action) => {
            delete state.tasks["new_task"]
            state.tasks[action.payload.id] = {
                task: {...action.payload},
                dataState: "success",
                error: null
            }
        })
        builder.addCase(createTask.rejected, (state, action) => {
            state.tasks["new_task"].dataState = "error"
            state.tasks["new_task"].error = action.error.message || "Unknown error"
        })
        //configurind editing actions
        builder.addCase(editTask.pending, (state, action) => {
            state.tasks[action.meta.arg.id].dataState = "loading"
            state.tasks[action.meta.arg.id].error = null
        })
        builder.addCase(editTask.fulfilled, (state, action) => {
            state.tasks[action.meta.arg.id] = {
                task: {...action.payload},
                dataState: "success",
                error: null
            }
        })
        builder.addCase(editTask.rejected, (state, action) => {
            state.tasks[action.meta.arg.id].dataState = "error",
            state.tasks[action.meta.arg.id].error = action.error.message || "Unknown error"
        })
        //configuring deleting actions
        builder.addCase(deleteTask.pending, (state, action) => {
            state.tasks[action.meta.arg.id].dataState = "loading"
            state.tasks[action.meta.arg.id].error = null
        })
        builder.addCase(deleteTask.fulfilled, (state, action) => {
            delete state.tasks[action.meta.arg.id]
        })
        builder.addCase(deleteTask.rejected, (state, action) => {
            state.tasks[action.meta.arg.id].dataState = "error",
            state.tasks[action.meta.arg.id].error = action.error.message || "Unknown error"
        })
    }
})

export const store = configureStore({
    reducer: {
        todo: slice.reducer
    }
})

export type StateType = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch