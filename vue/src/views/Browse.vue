<template>
  <b-container fluid>
    <b-row>
      <b-col cols="3">
        <Directories v-model="directory" />
      </b-col>
      <b-col cols="9">
        <FacetPills :directory="directory" @clear_directory="directory=null" />
        <PhotoGrid :directory="directory" />
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
// @ is an alias to /src
import PhotoGrid from "@/components/PhotoGrid.vue";
import FacetPills from "@/components/FacetPills.vue";
import Directories from "@/components/Directories.vue";
export default {
  name: "Browse",
  components: {
    PhotoGrid,
    FacetPills,
    Directories
  },
  data() {
    return { directory: null, max_year: 1950, min_year: 2020 };
  }
};
</script>
