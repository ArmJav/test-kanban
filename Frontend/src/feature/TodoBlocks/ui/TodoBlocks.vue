<script setup lang="ts">
interface Props {
  title?: String;
}

defineProps<Props>();
</script>

<template>
  <div>
    <p v-if="title">{{title}}</p>
    <div class="flex flex-wrap flex-col rounded-md shadow-sm border border-gray-200 min-w-[350px] min-h-[500px] p-2 text-[18px]">
      <slot name="zone">

      </slot>
    </div>
  </div>

</template>

<style scoped>

</style>