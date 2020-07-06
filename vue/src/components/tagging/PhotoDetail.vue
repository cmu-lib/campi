<template>
  <b-card v-if="!!photograph" header="Photo info">
    <b-row>
      <b-img :src="`${photograph.image.id}/full/!800,600/0/default.jpg`" />
    </b-row>
    <b-row align-v="center" align-h="between">
      <span>{{ photograph.filename }}</span>
      <b-badge variant="primary">
        <BIconFolderFill />
        {{ photograph.directory.label }}
      </b-badge>
      <b-badge variant="info" v-if="photograph.job">
        <BIconCamera />
        {{ photograph.job.label }}
      </b-badge>
    </b-row>
    <b-row>
      <b-button variant="primary" v-b-modal.add-tag>Add tag</b-button>
      <b-badge
        variant="warning"
        v-for="tag in photograph.photograph_tags"
        :key="tag.id"
      >{{ tag.tag.label }}</b-badge>
    </b-row>
    <b-modal id="add-tag" title="Add tag(s) to photograph" @ok="register_selected_tags">
      <b-form-select v-model="selected_tags" :options="tag_choices" multiple />
    </b-modal>
  </b-card>
</template>

<script>
import { HTTP } from "@/main";
import { BIconCamera, BIconFolderFill } from "bootstrap-vue";
export default {
  name: "PhotoDetail",
  components: {
    BIconCamera,
    BIconFolderFill
  },
  props: {
    photograph_id: {
      type: Number,
      required: true
    },
    available_tags: {
      type: Array
    }
  },
  data() {
    return {
      photograph: null,
      selected_tags: []
    };
  },
  computed: {
    tag_choices() {
      return this.available_tags.map(t => {
        return {
          text: t.label,
          value: t.id
        };
      });
    }
  },
  methods: {
    get_photograph() {
      HTTP.get(`photograph/${this.photograph_id}/`).then(
        response => {
          this.photograph = response.data;
          this.selected_tags = this.photograph.photograph_tags.map(
            t => t.tag.id
          );
        },
        error => {
          console.log(error);
        }
      );
    },
    register_selected_tags() {
      console.log(this.selected_tags);
      Promise.all(
        this.selected_tags.map(tag =>
          HTTP.post("tagging/photograph_tag/", {
            tag: tag,
            photograph: this.photograph.id
          })
        )
      ).then(onfulfilled => {
        this.get_photograph();
        console.log(onfulfilled);
      });
    }
  },
  mounted() {
    this.get_photograph();
  }
};
</script>