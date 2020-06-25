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
      console.log(photograph.id);
    }
  }
};
</script>