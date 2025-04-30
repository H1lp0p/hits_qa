import { createReducer, createSlice } from "@reduxjs/toolkit";
import { loadData } from "./thuks";
import { Pagination, TaskInfo } from "./resopnseBodies";

interface State {
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
        
        //configurind editing actions

        //configuring deleting actions
    }
})

//TODO: well, implement all other actions