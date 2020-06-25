<template>
  <b-container fluid>
    <PhotoBrowse @photo_click="photo_click" />
  </b-container>
</template>

<script>
import PhotoBrowse from "@/components/browsing/PhotoBrowse.vue";
export default {
  name: "TaggingSeedPhotoBrowse",
  components: { PhotoBrowse },
  props: {
    task_id: {
      type: Number,
      required: true
    }
  },
  methods: {
    photo_click(photograph) {
      this.$router.push({
        name: "TaggingExecution",
        params: { task_id: this.task_id, seed_photo_id: photograph.id }
      });
    }
  }
};
</script>