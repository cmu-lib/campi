<template>
  <b-container fluid>
    <b-row class="mt-2">
      <b-col cols="3">
        <h3>Filters</h3>
        <b-card class="my-2">
          <b-form-group
            label="Image text"
            description="Search for text detected within the image."
            label-size="sm"
          >
            <b-form-input size="sm" v-model="freetext" placeholder="e.g. mellon" debounce="1000" />
          </b-form-group>
        </b-card>
        <Tags
          v-model="tag"
          :directory="directory"
          :job="job"
          :gcv_object="gcv_object"
          :gcv_label="gcv_label"
          :digitized_date_range="digitized_date_range"
        />
        <Jobs
          v-model="job"
          :directory="directory"
          :tag="tag"
          :gcv_object="gcv_object"
          :gcv_label="gcv_label"
          :digitized_date_before="dd_before"
          :digitized_date_after="dd_after"
        />
        <GCVObjects
          v-model="gcv_object"
          :job="job"
          :directory="directory"
          :tag="tag"
          :gcv_label="gcv_label"
        />
        <GCVLabels
          v-model="gcv_label"
          :job="job"
          :directory="directory"
          :tag="tag"
          :gcv_object="gcv_object"
        />
        <Directories
          v-model="directory"
          :job="job"
          :tag="tag"
          :gcv_object="gcv_object"
          :gcv_label="gcv_label"
          :digitized_date_before="dd_before"
          :digitized_date_after="dd_after"
        />
      </b-col>
      <b-col cols="9">
        <FacetPills
          :freetext="freetext"
          :directory="directory"
          :digitized_date_range="digitized_date_range"
          :job="job"
          :tag="tag"
          :gcv_object="gcv_object"
          :gcv_label="gcv_label"
          @clear_directory="directory=null"
          @clear_job="job=null"
          @clear_tag="tag=null"
          @clear_gcv_object="gcv_object=null"
          @clear_gcv_label="gcv_label=null"
          @clear_freetext="freetext=''"
          @clear_date_range="reset_date()"
        />
        <PhotoGrid
          :per_page="42"
          :freetext="freetext"
          :directory="directory"
          :job="job"
          :tag="tag"
          :gcv_object="gcv_object"
          :gcv_label="gcv_label"
          :digitized_date_before="dd_before"
          :digitized_date_after="dd_after"
          @photo_click="photo_click"
        />
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import { HTTP } from "@/main";
import PhotoGrid from "@/components/browsing/PhotoGrid.vue";
import FacetPills from "@/components/browsing/FacetPills.vue";
import Directories from "@/components/browsing/Directories.vue";
import Jobs from "@/components/browsing/Jobs.vue";
import Tags from "@/components/browsing/Tags.vue";
import GCVObjects from "@/components/browsing/GCVObjects.vue";
import GCVLabels from "@/components/browsing/GCVLabels.vue";
export default {
  name: "PhotoBrowse",
  components: {
    PhotoGrid,
    FacetPills,
    Directories,
    Jobs,
    Tags,
    GCVObjects,
    GCVLabels,
  },
  data() {
    return {
      freetext: "",
      directory: null,
      job: null,
      tag: null,
      gcv_object: null,
      gcv_label: null,
      digitized_date_range: [2016, 2020],
    };
  },
  methods: {
    reset_date() {
      this.digitized_date_range = [2016, 2020];
    },
    photo_click(photograph) {
      this.$emit("photo_click", photograph);
    },
  },
  computed: {
    state_ids() {
      var ids = {};
      if (!!this.gcv_object) {
        ids["gcv_object"] = this.gcv_object.id;
      }
      if (!!this.gcv_label) {
        ids["gcv_label"] = this.gcv_label.id;
      }
      if (!!this.directory) {
        ids["directory"] = this.directory.id;
      }
      if (!!this.job) {
        ids["job"] = this.job.id;
      }
      if (!!this.tag) {
        ids["tag"] = this.tag.id;
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
    },
  },
  watch: {
    state_ids() {
      this.$router.push({ query: this.state_ids });
    },
  },
  mounted() {
    if (!!this.$route.query.directory) {
      return HTTP.get("/directory/" + this.$route.query.directory + "/").then(
        (results) => {
          this.directory = results.data;
        },
        (error) => {
          console.log(error);
        }
      );
    }

    if (!!this.$route.query.job) {
      return HTTP.get("/job/" + this.$route.query.job + "/").then(
        (results) => {
          this.job = results.data;
        },
        (error) => {
          console.log(error);
        }
      );
    }

    if (!!this.$route.query.tag) {
      return HTTP.get("/tagging/tag/" + this.$route.query.tag + "/").then(
        (results) => {
          this.tag = results.data;
        },
        (error) => {
          console.log(error);
        }
      );
    }

    if (!!this.$route.query.gcv_object) {
      return HTTP.get(
        "/gcv/object_annotation_labels_paginated/" +
          this.$route.query.gcv_object +
          "/"
      ).then(
        (results) => {
          this.gcv_object = results.data;
        },
        (error) => {
          console.log(error);
        }
      );
    }

    if (!!this.$route.query.gcv_label) {
      return HTTP.get(
        "/gcv/photo_labels/" + this.$route.query.gcv_label + "/"
      ).then(
        (results) => {
          this.gcv_label = results.data;
        },
        (error) => {
          console.log(error);
        }
      );
    }
  },
};
</script>
