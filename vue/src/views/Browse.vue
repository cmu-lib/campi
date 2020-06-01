<template>
  <b-container fluid>
    <b-row>
      <b-col cols="3">
        <JobTags
          v-model="job_tag"
          :directory="directory"
          :job="job"
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
          :job_tag="job_tag"
          :job="job"
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
          :per_page="42"
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
import { HTTP } from "../main";
import PhotoGrid from "@/components/PhotoGrid.vue";
import FacetPills from "@/components/FacetPills.vue";
import Directories from "@/components/Directories.vue";
import Jobs from "@/components/Jobs.vue";
import JobTags from "@/components/JobTags.vue";
export default {
  name: "Browse",
  components: {
    PhotoGrid,
    FacetPills,
    Directories,
    Jobs,
    JobTags
  },
  data() {
    return {
      directory: null,
      job: null,
      job_tag: null,
      digitized_date_range: [2016, 2020]
    };
  },
  methods: {
    reset_date() {
      this.digitized_date_range = [2016, 2020];
    }
  },
  computed: {
    state_ids() {
      var ids = {};
      if (!!this.directory) {
        ids["directory"] = this.directory.id;
      }
      if (!!this.job) {
        ids["job"] = this.job.id;
      }
      if (!!this.job_tag) {
        ids["job_tag"] = this.job_tag.id;
      }
      return ids;
    },
    dd_after() {
      if (this.digitized_date_range[0] != 2016) {
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
  },
  watch: {
    state_ids() {
      this.$router.push({ name: "Browse", query: this.state_ids });
    }
  },
  mounted() {
    if (!!this.$route.query.directory) {
      return HTTP.get("/directory/" + this.$route.query.directory + "/").then(
        results => {
          this.directory = results.data;
        },
        error => {
          console.log(error);
        }
      );
    }

    if (!!this.$route.query.job) {
      return HTTP.get("/job/" + this.$route.query.job + "/").then(
        results => {
          this.job = results.data;
        },
        error => {
          console.log(error);
        }
      );
    }

    if (!!this.$route.query.job_tag) {
      return HTTP.get("/job_tag/" + this.$route.query.job_tag + "/").then(
        results => {
          this.job_tag = results.data;
        },
        error => {
          console.log(error);
        }
      );
    }
  }
};
</script>
