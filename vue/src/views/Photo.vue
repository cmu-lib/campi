<template>
  <div v-if="!!image_data">
    <b-breadcrumb :items="directory_tree" />
    <b-row flex align-h="between" class="m-3">
      <b-link
        v-if="!!image_data.job"
        :to="{name: 'Browse', query: {job: image_data.job.id}}"
      >{{ job_display(image_data.job) }}</b-link>
      <span>Taken between: {{ image_data.date_taken_early }} - {{ image_data.date_taken_late }}</span>
      <span>File created: {{ image_data.digitized_date }}</span>
      <b-button
        size="sm"
        variant="success"
        :to="{name: 'Similarity', params: {id: image_data.id}}"
      >Find similar photos</b-button>
      <b-button size="sm" variant="primary" :href="image_data.image.full">Download full image</b-button>
    </b-row>
    <b-row>
      <IIIF :info_url="image_data.image.info" />
    </b-row>
  </div>
</template>

<script>
import IIIF from "@/components/IIIF";
import { HTTP } from "@/main";
export default {
  name: "Photo",
  components: {
    IIIF
  },
  props: {
    id: Number
  },
  data() {
    return {};
  },
  asyncComputed: {
    image_data() {
      return HTTP.get("/photograph/" + this.id + "/").then(
        results => {
          return results.data;
        },
        error => {
          console.log(error);
        }
      );
    }
  },
  computed: {
    directory_tree() {
      // Pass the immediate parent directory along with an empty array to dtree renderer
      var recursed_tree = this.render_dtree(
        this.image_data.directory,
        []
      ).reverse();
      // Push the photo name itself onto the end of the line
      const terminal = {
        text: this.image_data.filename
      };
      recursed_tree.push(terminal);
      return recursed_tree;
    }
  },
  methods: {
    render_dtree: function(d_obj, dtree) {
      const payload = {
        to: { name: "Browse", query: { directory: d_obj.id } },
        text: d_obj.label
      };
      dtree.push(payload);
      if (d_obj.parent_directory) {
        return this.render_dtree(d_obj.parent_directory, dtree);
      } else {
        return dtree;
      }
    },
    job_display(job) {
      if (job.label != job.job_code) {
        return job.label + " (" + job.job_code + ")";
      } else {
        return job.job_code + " (no descriptive title)";
      }
    }
  }
};
</script>
