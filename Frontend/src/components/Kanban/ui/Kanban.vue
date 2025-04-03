<script setup lang="ts">
import { ref } from 'vue';
import { Header } from '@/widget/Header';

interface Task {
  id: number;
  title: string;
}

type TaskStatus = 'todo' | 'inProgress' | 'done';

const open = ref<boolean>(false);

const statusLabels: Record<TaskStatus, string> = {
  todo: 'Беклог',
  inProgress: 'В процессе',
  done: 'Выполнен'
};

const taskColumns = ref<Record<TaskStatus, Task[]>>({
  todo: [
    { id: 1, title: 'Task 1' },
    { id: 2, title: 'Task 2' }
  ],
  inProgress: [],
  done: []
});

let draggedTask: Task | null = null;

const onDragStart = (task: Task) => {
  draggedTask = task;
};

const onDrop = (event: DragEvent, status: TaskStatus) => {
  if (draggedTask) {
    Object.keys(taskColumns.value).forEach((key) => {
      taskColumns.value[key as TaskStatus] = taskColumns.value[key as TaskStatus].filter(t => t.id !== draggedTask!.id);
    });
    taskColumns.value[status].push(draggedTask);
    draggedTask = null;
  }
};

const handleOk = () => {
  console.log('Model open');
  
}
</script>



<template>
  <Header></Header>
  <div class="board mt-5">
    <a-modal v-model:open="open" title="Добавить задачу" @ok="handleOk">
      <p>Some contents...</p>
      <p>Some contents...</p>
      <p>Some contents...</p>
    </a-modal>
    <div v-for="(tasks, status) in taskColumns" :key="status" class="column" @dragover.prevent @drop="onDrop($event, status)">
      <h3 class="text-2xl">{{ statusLabels[status] }}</h3>
      <a-divider></a-divider>
      <div class="task-list">
        <div v-for="task in tasks" :key="task.id"  draggable="true" @dragstart="onDragStart(task)">
          <div class="task">
            {{ task.title }}
          </div>

        </div>
        <button class="cursor-pointer text-blue-500 hover:drop-shadow-xl hover:scale-102 transition duration-100 ease-in-out" @click="open = !open">+ Добавить</button>
      </div>
    </div>
  </div>
</template>



<style scoped>
.board {
  display: flex;
  gap: 20px;
  justify-content: space-between

}

.column {
  width: 400px;
  background: #f4f4f4;
  padding: 10px;
  border-radius: 5px;
  min-height: 150px;
}

.task-list {
  min-height: 100px;
}

.task {
  padding: 10px;
  background: white;
  border: 1px solid #ddd;
  margin-bottom: 5px;
  border-radius: 5px;
  cursor: grab;
}
</style>
