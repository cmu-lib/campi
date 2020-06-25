<template>
  <b-container fluid>
    <TaggingWorkflowNav />
    <PhotoBrowse />
  </b-container>
</template>

<script>
import TaggingWorkflowNav from "@/components/tagging/TaggingWorkflowNav.vue";
import PhotoBrowse from "@/components/browsing/PhotoBrowse.vue";
export default {
  name: "TaggingSeedPhotoBrowse",
  components: { TaggingWorkflowNav, PhotoBrowse },
  props: {
    task_id: {
      type: Number,
      required: true
    }
  }
};
</script>