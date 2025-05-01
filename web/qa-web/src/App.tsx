import { useState } from 'react'
import './App.css'
import { Provider, useSelector } from 'react-redux'
import { State, store } from './domain/store'
import { TaskContainer } from './components/taskContainer/taskContainer'

function App() {
  return (
    <>
       <Provider store={store}>
          <TaskContainer/>
       </Provider>
    </>
  )
}

export default App
