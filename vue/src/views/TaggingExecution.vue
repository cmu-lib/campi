<template>
  <div>
    <p>Now let's get tagging with task {{ task_id }} on seed photo {{ seed_photo_id }}</p>
  </div>
</template>

<script>
export default {
  name: "TaggingExecution",
  props: {
    task_id: {
      type: Number,
      required: true
    },
    seed_photo_id: {
      type: Number,
      required: true
    }
  }
};
</script>