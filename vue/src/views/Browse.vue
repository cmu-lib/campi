<template>
  <b-container fluid>
    <b-row>
      <b-col cols="3">
        <DigitizedDate v-model="digitized_date_range" :directory="directory" />
        <Directories
          v-model="directory"
          :digitized_date_before="dd_before"
          :digitized_date_after="dd_after"
        />
      </b-col>
      <b-col cols="9">
        <FacetPills
          :directory="directory"
          :digitized_date_range="digitized_date_range"
          @clear_directory="directory=null"
          @clear_date_range="reset_date()"
        />
        <PhotoGrid
          :directory="directory"
          :digitized_date_before="dd_before"
          :digitized_date_after="dd_after"
        />
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
// @ is an alias to /src
import PhotoGrid from "@/components/PhotoGrid.vue";
import FacetPills from "@/components/FacetPills.vue";
import Directories from "@/components/Directories.vue";
import DigitizedDate from "@/components/DigitizedDate.vue";
export default {
  name: "Browse",
  components: {
    PhotoGrid,
    FacetPills,
    Directories,
    DigitizedDate
  },
  data() {
    return { directory: null, digitized_date_range: [2003, 2020] };
  },
  methods: {
    reset_date() {
      this.digitized_date_range = [2003, 2020];
    }
  },
  computed: {
    dd_after() {
      if (this.digitized_date_range[0] != 2003) {
        return this.digitized_date_range[0];
      }
      return null;
    },
    dd_before() {
      if (this.digitized_date_range[1] != 2020) {
        return this.digitized_date_range[1];
      }
      return null;
    }
  }
};
</script>
