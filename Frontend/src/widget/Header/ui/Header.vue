<script setup lang="ts">
import { UserOutlined } from '@ant-design/icons-vue';
import router from "@/router";


</script>

<template>
  <div class="flex justify-between items-end text-gray-400 text-2xl">
    <h1 class="">Разработка</h1>
    <UserOutlined class="cursor-pointer" @click="router.push('/catalog')"/>
  </div>
</template>

<style scoped>

</style>