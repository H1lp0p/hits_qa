import { configureStore, createReducer, createSlice } from "@reduxjs/toolkit";
import { createTask, deleteTask, editTask, loadData } from "./thuks";
import { Pagination, TaskInfo } from "./resopnseBodies";


export interface State {
    tasks: TaskInfo[],
    pagination: Pagination | null,
    dataState: "loading" | "error" | "success",
    error: string | null,
}

const initState: State = {
    tasks : [],
    pagination: null,
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
            state.tasks = action.payload.tasks
            state.pagination = action.payload.pagination
        })
        builder.addCase(loadData.rejected, (state, action) => {
            state.dataState = "error"
            state.error = action.error.message || "Unknown error"
        })
        //configuring creating actions
        builder.addCase(createTask.pending, (state, action) => {
            //well, just in case
        })
        builder.addCase(createTask.fulfilled, (state, action) => {
            state.tasks = [...state.tasks, action.payload]
        })
        builder.addCase(createTask.rejected, (state, action) => {
            state.dataState = 'error'
            state.error = action.error.message || "Unknown error"
        })
        //configurind editing actions
        builder.addCase(editTask.pending, (state, action) => {
            //well, just in case
        })
        builder.addCase(editTask.fulfilled, (state, action) => {
            state.tasks = state.tasks.filter((it) => it.id != action.meta.arg.id)
            state.tasks = [...state.tasks, action.payload]
        })
        builder.addCase(editTask.rejected, (state, action) => {
            state.dataState = 'error'
            state.error = action.error.message || "Unknown error"
        })
        //configuring deleting actions
        builder.addCase(deleteTask.pending, (state, action) => {
            //well, just in case
        })
        builder.addCase(deleteTask.fulfilled, (state, action) => {
            state.tasks = state.tasks.filter((it) => it.id != action.meta.arg.id)
        })
        builder.addCase(deleteTask.rejected, (state, action) => {
            state.dataState = 'error'
            state.error = action.error.message || "Unknown error"
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
//TODO: well, implement all other actions