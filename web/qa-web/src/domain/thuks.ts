import { createAsyncThunk } from "@reduxjs/toolkit";
import { Ordering, OrderingType } from "../data/pagination";
import axios from "axios";
import { apiUrl } from "../common/config";
import { Error } from "../common/error";
import { TaskInfo, TaskList } from "./resopnseBodies";
import { CreateTaskModel, EditTaskModel, TaskListQuery } from "./requestBodies";

const get_all = apiUrl + "/tasks/all"
const task_list =  apiUrl + "/tasks/list"
const single_task_actions = (id: string) => apiUrl + `/tasks/${id}`
const create_task = apiUrl + "/tasks"


export const loadData = createAsyncThunk(
    "load",
    async (
        data: TaskListQuery = {
            ordering: Ordering.priority,
            orderingType: OrderingType.asc,
            page: 1,
            pageSize: 5,
    }
    , {rejectWithValue}) => {
        try{
            const response = await axios.get<TaskList>(task_list, {
                params: {
                    orderign: data.ordering,
                    ordering_type: data.orderingType,
                    page: data.page,
                    page_size: data.pageSize,
                }
            })
            return response.data
        }
        catch (error) {
            if (axios.isAxiosError(error)){
                const er: Error = {
                    status: error.response?.status,
                    payload: error.response?.data,
                    message: "Response Error"
                }
                return rejectWithValue(er)
            }
        }
        return rejectWithValue({
            status: -1,
            message: "internal Error",
            payload: null,
        })
    }
)

export const createTask = createAsyncThunk(
    "create",
    async (data: CreateTaskModel, {rejectWithValue}) => {
        try{
            const response = await axios.post<TaskInfo>(create_task, data)
            return response
        }
        catch (error) {
            if (axios.isAxiosError(error)){
                const er: Error = {
                    status: error.response?.status,
                    payload: error.response?.data,
                    message: "Response Error"
                }
                rejectWithValue(er)
            }
        }
    }
)

export const editTask = createAsyncThunk(
    "edit",
    async (data: {editData: EditTaskModel, id: string}, {rejectWithValue}) => {
        try{
            const response = await axios.put<TaskInfo>(
                single_task_actions(data.id),
                data.editData
            )
            return response
        }
        catch (error) {
            if (axios.isAxiosError(error)){
                const er: Error = {
                    status: error.response?.status,
                    payload: error.response?.data,
                    message: "Response Error"
                }
                rejectWithValue(er)
            }
        }    
    }
)

export const deleteTask = createAsyncThunk(
    "delete",
    async (data: {id: string}, {rejectWithValue}) => {
        try{
            const response =  await axios.delete(
                single_task_actions(data.id)
            )
            return response
        }
        catch (error) {
            if (axios.isAxiosError(error)){
                const er: Error = {
                    status: error.response?.status,
                    payload: error.response?.data,
                    message: "Response Error"
                }
                rejectWithValue(er)
            }
        }
    }
)