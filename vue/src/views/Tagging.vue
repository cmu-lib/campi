<template>
  <b-container fluid>
    <TaggingWorkflowNav />
    <router-view />
  </b-container>
</template>

<script>
import TaggingWorkflowNav from "@/components/tagging/TaggingWorkflowNav.vue";
export default {
  name: "Tagging",
  components: { TaggingWorkflowNav }
};
</script>