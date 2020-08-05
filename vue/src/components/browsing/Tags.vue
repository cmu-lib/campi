<template>
  <b-card class="my-2" no-body>
    <template v-slot:header>
      <b-row align-h="between" align-v="center" class="mx-1">
        <span>
          Tags
          <BIconQuestionCircle
            title="Tags created by CMU Archives and applied by humans."
            v-b-tooltip:hover
            class="mx-1"
          />
        </span>
        <BIconCaretDownFill v-if="open" class="pointer" @click="open=!open" />
        <BIconCaretLeftFill v-else class="pointer" @click="open=!open" />
      </b-row>
    </template>
    <b-collapse v-model="open">
      <b-input-group class="p-2">
        <b-input v-model="tag_label_search" debounce="500" placeholder="Search tag names..." />
        <b-input-group-append v-if="tag_label_search != ''">
          <b-button variant="warning" size="sm" @click="tag_label_search=''">
            <BIconXSquare />
          </b-button>
        </b-input-group-append>
      </b-input-group>
      <b-list-group v-if="!!tags" flush>
        <b-list-group-item
          v-for="tag in tags"
          :key="tag.id"
          class="d-flex justify-content-between align-items-center my-0 py-1 mr-0 pr-0"
        >
          <span class="text-truncate pointer" @click="select_tag(tag)">{{ tag.label }}</span>
          <b-badge variant="info" class="ml-auto mr-1">{{ tag.n_images }}</b-badge>
        </b-list-group-item>
        <b-list-group-item
          v-if="additional_tags"
          class="my-0 py-1 mr-0 pr-0 pointer"
          @click="show_more"
          variant="secondary"
        >Show more...</b-list-group-item>
      </b-list-group>
    </b-collapse>
  </b-card>
</template>

<script>
import { HTTP } from "@/main";
import {
  BIconXSquare,
  BIconCaretLeftFill,
  BIconCaretDownFill,
  BIconQuestionCircle,
} from "bootstrap-vue";
export default {
  name: "Tags",
  components: {
    BIconXSquare,
    BIconCaretLeftFill,
    BIconCaretDownFill,
    BIconQuestionCircle,
  },
  props: {
    digitized_date_before: {
      type: Number,
      default: null,
    },
    digitized_date_after: {
      type: Number,
      default: null,
    },
    page_size: {
      type: Number,
      default: 10,
    },
    job: {
      type: Object,
      default: null,
    },
    directory: {
      type: Object,
      default: null,
    },
    gcv_object: {
      type: Object,
      default: null,
    },
    gcv_label: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      show_total: 10,
      tag_label_search: "",
      additional_tags: true,
      open: false,
    };
  },
  computed: {
    query_payload() {
      var payload = {
        ordering: "-n_images,label",
        limit: this.show_total,
      };
      if (this.tag_label_search != "") {
        payload["text"] = this.tag_label_search;
      }
      if (!!this.job) {
        payload["job"] = this.job.id;
      }
      if (!!this.gcv_object) {
        payload["gcv_object"] = this.gcv_object.id;
      }
      if (!!this.gcv_label) {
        payload["gcv_label"] = this.gcv_label.id;
      }
      if (!!this.directory) {
        payload["directory"] = this.directory.id;
      }
      if (!!this.digitized_date_after) {
        payload["digitized_date_after"] = `${this.digitized_date_after}-01-01`;
      }
      if (!!this.digitized_date_before) {
        payload[
          "digitized_date_before"
        ] = `${this.digitized_date_before}-01-01`;
      }
      return payload;
    },
  },
  asyncComputed: {
    tags() {
      return HTTP.get("/tagging/tag/", {
        params: this.query_payload,
      }).then(
        (results) => {
          if (!!results.data.next) {
            this.additional_tags = true;
          } else {
            this.additional_tags = false;
          }
          return results.data.results;
        },
        (error) => {
          console.log(error);
        }
      );
    },
  },
  methods: {
    show_more() {
      this.show_total += this.page_size;
    },
    select_tag(tag) {
      this.$emit("input", tag);
      window.scrollTo(0, 0);
    },
  },
};
</script>