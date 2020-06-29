<template>
  <b-card class="my-2" header="Job Tags">
    <b-input-group class="my-2">
      <b-input v-model="job_tag_label_search" debounce="500" placeholder="Search tag names..." />
      <b-input-group-append v-if="job_tag_label_search != ''">
        <b-button variant="warning" size="sm" @click="job_tag_label_search=''">
          <BIconXSquare />
        </b-button>
      </b-input-group-append>
    </b-input-group>
    <b-list-group v-if="!!job_tags">
      <b-list-group-item
        v-for="job_tag in job_tags"
        :key="job_tag.id"
        class="d-flex justify-content-between align-items-center my-0 py-1 mr-0 pr-0"
        @click="select_job_tag(job_tag)"
      >
        <span class="text-truncate">{{ job_tag.label }}</span>
        <b-badge variant="info" class="ml-auto mr-1">{{ job_tag.n_images }}</b-badge>
      </b-list-group-item>
      <b-list-group-item
        v-if="additional_job_tags"
        class="my-0 py-1 mr-0 pr-0"
        @click="show_more"
        variant="secondary"
      >Show more...</b-list-group-item>
    </b-list-group>
  </b-card>
</template>

<script>
import { HTTP } from "@/main";
import { BIconXSquare } from "bootstrap-vue";
export default {
  name: "JobTags",
  components: {
    BIconXSquare
  },
  props: {
    job_tag: {
      type: Object,
      default: null
    },
    directory: {
      type: Object,
      default: null
    },
    job: {
      type: Object,
      default: null
    },
    tag: {
      type: Object,
      default: null
    },
    digitized_date_before: {
      type: Number,
      default: null
    },
    digitized_date_after: {
      type: Number,
      default: null
    },
    page_size: {
      type: Number,
      default: 10
    }
  },
  data() {
    return {
      show_total: 10,
      job_tag_label_search: "",
      additional_job_tags: true
    };
  },
  computed: {
    query_payload() {
      var payload = {
        ordering: "-n_images,label",
        limit: this.show_total
      };
      if (this.job_tag_label_search != "") {
        payload["label"] = this.job_tag_label_search;
      }
      if (!!this.job) {
        payload["job"] = this.job.id;
      }
      if (!!this.directory) {
        payload["directory"] = this.directory.id;
      }
      if (!!this.tag) {
        payload["tag"] = this.tag.id;
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
    }
  },
  asyncComputed: {
    job_tags() {
      return HTTP.get("/job_tag/", {
        params: this.query_payload
      }).then(
        results => {
          if (!!results.data.next) {
            this.additional_job_tags = true;
          } else {
            this.additional_job_tags = false;
          }
          return results.data.results;
        },
        error => {
          console.log(error);
        }
      );
    }
  },
  methods: {
    show_more() {
      this.show_total += this.page_size;
    },
    select_job_tag(job_tag) {
      this.$emit("input", job_tag);
      window.scrollTo(0, 0);
    }
  }
};
</script>