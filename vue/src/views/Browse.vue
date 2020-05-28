<template>
  <BrowseInterface :directory="directory" :job="job" :job_tag="job_tag" />
</template>

<script>
// @ is an alias to /src
import { HTTP } from "../main";
import BrowseInterface from "@/components/BrowseInterface.vue";
export default {
  name: "Browse",
  components: {
    PhotoGrid,
    FacetPills,
    Directories,
    Jobs,
    JobTags
  },
  props: {
    directory_id: {
      type: Number,
      default: null
    },
    job_id: {
      type: Number,
      default: null
    },
    job_tag_id: {
      type: Number,
      default: null
    }
  },
  asyncComputed: {
    directory() {
      if (!!directory_id) {
        return HTTP.get("/directory/" + this.directory_id + "/").then(
          results => {
            return results.data;
          },
          error => {
            console.log(error);
          }
        );
      } else {
        return null;
      }
    },
    job() {
      if (!!job_id) {
        return HTTP.get("/job/" + this.job_id + "/").then(
          results => {
            return results.data;
          },
          error => {
            console.log(error);
          }
        );
      } else {
        return null;
      }
    },
    job_tag() {
      if (!!job_tag_id) {
        return HTTP.get("/job_id/" + this.job_tag_id + "/").then(
          results => {
            return results.data;
          },
          error => {
            console.log(error);
          }
        );
      } else {
        return null;
      }
    }
  }
};
</script>
