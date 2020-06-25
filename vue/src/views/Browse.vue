<template>
  <PhotoBrowse @photo_click="photo_click" />
</template>

<script>
import PhotoBrowse from "@/components/browsing/PhotoBrowse.vue";
export default {
  name: "Browse",
  components: {
    PhotoBrowse
  },
  methods: {
    photo_click(photograph) {
      this.$router.push({ name: "Photo", params: { id: photograph.id } });
    }
  }
};
</script>
