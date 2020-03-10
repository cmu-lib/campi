<template>
  <b-container fluid>
    <PhotoGrid />
  </b-container>
</template>

<script>
// @ is an alias to /src
import PhotoGrid from "@/components/PhotoGrid.vue";

export default {
  name: "Home",
  components: {
    PhotoGrid
  }
};
</script>
