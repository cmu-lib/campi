<template>
  <b-card class="my-2" no-body>
    <template v-slot:header>
      <b-row align-h="between" align-v="center" class="mx-1">
        <span>
          GCV Labels
          <BIconQuestionCircle
            title="These are labels added to photographs by Google's generic image description API."
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
        <b-input
          v-model="gcvlabel_label_search"
          debounce="500"
          placeholder="Search GCV label names..."
        />
        <b-input-group-append v-if="gcvlabel_label_search != ''">
          <b-button variant="warning" size="sm" @click="gcvlabel_label_search=''">
            <BIconXSquare />
          </b-button>
        </b-input-group-append>
      </b-input-group>
      <b-list-group v-if="!!gcvlabels" flush>
        <b-list-group-item
          v-for="gcvlabel in gcvlabels"
          :key="gcvlabel.id"
          class="d-flex justify-content-between align-items-center my-0 py-1 mr-0 pr-0"
        >
          <span
            class="text-truncate pointer"
            @click="select_gcvlabel(gcvlabel)"
          >{{ gcvlabel.label }}</span>
          <b-badge variant="info" class="ml-auto mr-1">{{ gcvlabel.n_images }}</b-badge>
        </b-list-group-item>
        <b-list-group-item
          v-if="additional_gcvlabels"
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
  name: "GCVLabels",
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
    tag: {
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
  },
  data() {
    return {
      show_total: 10,
      gcvlabel_label_search: "",
      additional_gcvlabels: true,
      open: false,
    };
  },
  computed: {
    query_payload() {
      var payload = {
        ordering: "-n_images,label",
        limit: this.show_total,
      };
      if (this.gcvlabel_label_search != "") {
        payload["label"] = this.gcvlabel_label_search;
      }
      if (!!this.job) {
        payload["job"] = this.job.id;
      }
      if (!!this.tag) {
        payload["tag"] = this.tag.id;
      }
      if (!!this.directory) {
        payload["directory"] = this.directory.id;
      }
      if (!!this.gcv_object) {
        payload["gcv_object"] = this.gcv_object.id;
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
    gcvlabels() {
      return HTTP.get("/gcv/photo_labels/", {
        params: this.query_payload,
      }).then(
        (results) => {
          if (!!results.data.next) {
            this.additional_gcvlabels = true;
          } else {
            this.additional_gcvlabels = false;
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
    select_gcvlabel(gcvlabel) {
      this.$emit("input", gcvlabel);
      window.scrollTo(0, 0);
    },
  },
};
</script>