<template>
  <b-container>
    <b-card no-body>
      <template v-slot:header>
        <b-row align-h="between" class="mx-2">
          <h2>Tags</h2>
          <span>
            <b-form-group label="Order" id="tag-order-menu-info">
              <b-form-select
                id="tag-order-menu"
                v-model="tag_ordering"
                :options="tag_ordering_options"
              />
            </b-form-group>
            <b-button v-b-modal.new-tag-modal variant="primary">New tag</b-button>
          </span>
        </b-row>
        <b-modal id="new-tag-modal" @ok="create_tag">
          <b-form-group label="New tag label" id="tag-label-input-info">
            <b-form-input id="tag-label-input" v-model="new_tag_label" />
          </b-form-group>
        </b-modal>
      </template>
      <b-list-group flush v-if="!!tags">
        <b-list-group-item
          v-for="tag in tags"
          :key="tag.id"
          class="d-flex justify-content-between align-items-center"
        >
          <span>{{ tag.label }}</span>
          <span>
            <BIconXCircleFill variant="secondary" @click="delete_tag(tag)" />
          </span>
        </b-list-group-item>
      </b-list-group>
    </b-card>
  </b-container>
</template>

<script>
import { HTTP } from "@/main";
import { BIconXCircleFill } from "bootstrap-vue";
export default {
  name: "Tags",
  components: { BIconXCircleFill },
  data() {
    return {
      tags: [],
      new_tag_label: null,
      tag_ordering: "label"
    };
  },
  computed: {
    tag_ordering_options() {
      return [
        { value: "label", text: "A-Z" },
        { value: "-label", text: "Z-A" },
        { value: "n_images", text: "Times used (asc)" },
        { value: "-n_images", text: "Times used (dsc)" }
      ];
    }
  },
  methods: {
    get_tags() {
      return HTTP.get("/tagging/tag/").then(
        results => {
          this.tags = results.data.results;
        },
        error => {
          console.log(error.response);
          this.$bvToast.toast({
            message: error.response,
            options: { variant: "danger" }
          });
        }
      );
    },
    create_tag() {
      HTTP.post("/tagging/tag/", { label: this.new_tag_label }).then(
        results => {
          this.tags.push(results.data);
          this.get_tags();
          this.new_tag_label = null;
        },
        error => {
          this.$bvToast.toast(error.data, {
            title: "Error",
            variant: "danger"
          });
          this.new_tag_label = null;
        }
      );
    },
    delete_tag(tag) {
      HTTP.delete(`/tagging/tag/${tag.id}/`).then(
        results => {
          this.$bvToast.toast(results.status, {
            title: `"${tag.label}" deleted`,
            variant: "success"
          });
          this.get_tags();
        },
        error => {
          console.log(error);
        }
      );
    }
  },
  created() {
    this.get_tags();
  }
};
</script>