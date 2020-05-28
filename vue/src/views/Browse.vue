<template>
  <b-container fluid>
    <b-row>
      <b-col cols="3">
        <DigitizedDate v-model="digitized_date_range" :directory="directory" />
        <JobTags
          v-model="job_tag"
          :directory="directory"
          :digitized_date_range="digitized_date_range"
        />
        <Jobs
          v-model="job"
          :job_tag="job_tag"
          :directory="directory"
          :digitized_date_before="dd_before"
          :digitized_date_after="dd_after"
        />
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
          :job="job"
          :job_tag="job_tag"
          @clear_directory="directory=null"
          @clear_job="job=null"
          @clear_job_tag="job_tag=null"
          @clear_date_range="reset_date()"
        />
        <PhotoGrid
          :directory="directory"
          :job="job"
          :job_tag="job_tag"
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
import Jobs from "@/components/Jobs.vue";
import JobTags from "@/components/JobTags.vue";
export default {
  name: "Browse",
  components: {
    PhotoGrid,
    FacetPills,
    Directories,
    DigitizedDate,
    Jobs,
    JobTags
  },
  data() {
    return {
      directory: null,
      job: null,
      job_tag: null,
      digitized_date_range: [2003, 2020]
    };
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
