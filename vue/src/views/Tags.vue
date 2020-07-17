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
          <span>
            <BIconPencil @click="tag_edit_init(tag)" />
            {{ tag.label }}
          </span>
          <b-modal :id="`edit-tag-${tag.id}`" @ok="edit_tag(tag)">
            <b-form-group label="Edit tag label" id="tag-label-edit-info">
              <b-form-input id="tag-label-edit" v-model="tag_edit_label" />
            </b-form-group>
          </b-modal>
          <span>
            <b-badge class="mx-3">{{ tag.n_images }} photos</b-badge>
            <BIconXCircleFill variant="secondary" @click="$bvModal.show(`delete-tag-${tag.id}`)" />
            <b-modal
              :id="`delete-tag-${tag.id}`"
              @ok="delete_tag(tag)"
              ok-title="Delete"
              ok-variant="danger"
            >Delete "{{ tag.label}}"? It will be removed from every photo it is attached to and can't be undone.</b-modal>
          </span>
        </b-list-group-item>
      </b-list-group>
    </b-card>
  </b-container>
</template>

<script>
import { HTTP } from "@/main";
import { BIconXCircleFill, BIconPencil } from "bootstrap-vue";
export default {
  name: "Tags",
  components: { BIconXCircleFill, BIconPencil },
  data() {
    return {
      tags: [],
      new_tag_label: null,
      tag_edit_label: null,
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
      return HTTP.get("/tagging/tag/", {
        params: { ordering: this.tag_ordering }
      }).then(
        results => {
          this.tags = results.data.results;
        },
        error => {
          this.$bvToast.toast({
            message: error.response,
            options: { variant: "danger" }
          });
        }
      );
    },
    tag_edit_init(tag) {
      this.tag_edit_label = tag.label;
      this.$bvModal.show(`edit-tag-${tag.id}`);
    },
    create_tag() {
      HTTP.post("/tagging/tag/", { label: this.new_tag_label }).then(
        results => {
          this.tags.push(results.data);
          this.get_tags();
          this.new_tag_label = null;
        },
        error => {
          this.$bvToast.toast(error.response.data.label, {
            title: "Error",
            variant: "danger"
          });
          this.new_tag_label = null;
        }
      );
    },
    edit_tag(tag) {
      HTTP.patch(`/tagging/tag/${tag.id}/`, {
        label: this.tag_edit_label
      }).then(
        results => {
          this.$bvToast.toast(results.status, {
            title: `"${tag.label}" updated`,
            variant: "success"
          });
          this.get_tags();
        },
        error => {
          this.$bvToast.toast(error.response.data.label, {
            title: "Error",
            variant: "danger"
          });
          this.tag_edit_label = null;
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
  },
  watch: {
    tag_ordering() {
      this.get_tags();
    }
  }
};
</script>