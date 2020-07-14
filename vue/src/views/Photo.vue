<template>
  <b-container fluid v-if="!!image_data">
    <b-breadcrumb :items="directory_tree" />
    <b-row flex align-h="between" class="m-1">
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
      <b-form-checkbox
        v-model="show_annotations"
        name="check-button"
        switch
        v-b-tooltip.hover
        title="Show annotations of faces, objects, and text recognized from regions in this image."
      >Show annotations</b-form-checkbox>
    </b-row>
    <b-row class="m-1" align-v="center" align-h="between">
      <h5>
        <b-button size="sm" variant="secondary" v-b-modal.add-tag>Edit tags</b-button>
        <b-badge
          v-for="tag in image_data.photograph_tags"
          :key="tag.id"
          variant="warning"
          class="mx-1"
          :to="{name: 'Browse', query: {tag: tag.tag.id}}"
        >
          <BIconTag class="mr-1" />
          {{ tag.tag.label }}
        </b-badge>
      </h5>
      <h5>
        <b-badge
          v-if="!!image_data.job"
          variant="info"
          class="mx-1"
          :to="{name: 'Browse', query: {job: image_data.job.id}}"
        >
          <BIconCamera class="mr-1" />
          {{ image_data.job.label }}
        </b-badge>
        <b-badge
          variant="primary"
          class="mx-1"
          :to="{name: 'Browse', query: {directory: image_data.directory.id}}"
        >
          <BIconFolderFill class="mr-1" />
          {{ image_data.directory.label }}
        </b-badge>
      </h5>
      <b-modal id="add-tag" title="Add tag(s) to photograph" @ok="register_tag_changes">
        <p>Shift-click to select multiple tags. Option-click to deselct a tag.</p>
        <b-form-select
          v-if="!!tag_choices"
          v-model="selected_tags"
          :options="tag_choices"
          multiple
          :select-size="20"
        />
      </b-modal>
    </b-row>
    <b-row>
      <IIIF :key="iiif_key" :info_url="image_data.image.info" :annotations="annotations" />
    </b-row>
  </b-container>
</template>

<script>
import IIIF from "@/components/IIIF";
import _ from "lodash";
import { HTTP } from "@/main";
import { BIconTag, BIconCamera, BIconFolderFill } from "bootstrap-vue";
export default {
  name: "Photo",
  components: {
    IIIF,
    BIconTag,
    BIconCamera,
    BIconFolderFill
  },
  props: {
    id: Number
  },
  data() {
    return {
      show_annotations: false,
      iiif_key: 1,
      selected_tags: [],
      image_data: null,
      tag_choices: null
    };
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
    },
    annotations() {
      var anns = [];
      if (!!this.image_data && this.show_annotations) {
        this.image_data.faceannotation.map(f => {
          var fann = this.pixels(f);
          fann["className"] = "face-annotation";
          fann["id"] = `face-${f.id}`;
          fann["title"] = `face-${f.detection_confidence}`;
          anns.push(fann);
        });
        this.image_data.objectannotation.map(o => {
          var oann = this.pixels(o);
          oann["className"] = "object-annotation";
          oann["id"] = `object-${o.id}`;
          oann["title"] = `object-${o.label}`;
          anns.push(oann);
        });
      }
      return anns;
    },
    new_tags() {
      // Tags to be added that aren't already attached to this photograph
      return _.difference(
        this.selected_tags,
        this.image_data.photograph_tags.map(t => t.tag.id)
      );
    },
    deletable_tags() {
      // Tags to be deleted that are on the current photo but aren't in the selected tags
      return _.difference(
        this.image_data.photograph_tags.map(t => t.tag.id),
        this.selected_tags
      );
    }
  },
  methods: {
    get_image_data() {
      HTTP.get("/photograph/" + this.id + "/").then(
        results => {
          this.image_data = results.data;
          this.selected_tags = this.image_data.photograph_tags.map(
            pt => pt.tag.id
          );
        },
        error => {
          console.log(error);
        }
      );
    },
    get_available_tags() {
      HTTP.get("tagging/tag/").then(
        response => {
          this.tag_choices = response.data.results.map(t => {
            return {
              text: t.label,
              value: t.id
            };
          });
        },
        error => {
          console.log(error);
        }
      );
    },
    pixels(annotation) {
      return {
        px: annotation.x,
        py: annotation.y,
        width: annotation.width,
        height: annotation.height
      };
    },
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
    },
    add_tag(photograph_id, tag_id) {
      // Adding an arbitrary, non-task tag
      HTTP.post("tagging/photograph_tag/", {
        tag: tag_id,
        photograph: photograph_id
      }).then(
        response => {
          const newtag = _.find(this.tag_choices, { value: tag_id });
          this.image_data.photograph_tags.push({
            id: response.data.id,
            tag: { id: newtag.value, label: newtag.text }
          });
        },
        error => {
          console.log(error);
        }
      );
    },
    remove_tag(photograph_id, tag_id) {
      // Removing an arbitrary, non-task tag
      const photograph_tag_id = _.find(
        this.image_data.photograph_tags,
        pt => pt.tag.id == tag_id
      ).id;
      HTTP.delete(`tagging/photograph_tag/${photograph_tag_id}/`).then(
        response => {
          console.log(response);
          const pt_index = _.findIndex(this.image_data.photograph_tags, {
            id: photograph_tag_id
          });
          this.image_data.photograph_tags.splice(pt_index, 1);
        },
        error => {
          console.log(error);
        }
      );
    },
    register_selected_tags() {
      Promise.all(
        this.new_tags.map(tag => this.add_tag(this.image_data.id, tag))
      ).then(onfulfilled => {
        console.log(onfulfilled);
      });
    },
    delete_deselected_tags() {
      Promise.all(
        this.deletable_tags.map(tag => this.remove_tag(this.image_data.id, tag))
      ).then(onfulfilled => {
        console.log(onfulfilled);
      });
    },
    register_tag_changes() {
      this.delete_deselected_tags();
      this.register_selected_tags();
    }
  },
  watch: {
    show_annotations() {
      // HACKY Force IIIF component to update by incrementing its VNode key
      this.iiif_key += 1;
    }
  },
  mounted() {
    this.get_image_data();
    this.get_available_tags();
  }
};
</script>
