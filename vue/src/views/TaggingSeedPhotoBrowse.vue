<template>
  <b-container fluid>
    <p>Select a "seed photo" that will serve as the starting point of tagging. The server will find visually-similar photos to this one to help prioritize the photos and jobs that you will look through.</p>
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